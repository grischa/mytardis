import collections
import os

from collections import defaultdict
from django.conf import settings
from django.utils.module_loading import import_string

from tardis.data_organisation.path_encoding import path_string_escape, \
    whitespace_to_underscores
from tardis.tardis_portal.models import DataFile, Dataset, Experiment
from tardis.tardis_portal.util import split_path

DEFAULT_PATH_MAPPER = getattr(settings, 'DEFAULT_PATH_MAPPER', 'deep-storage')


class PathTranslationError(Exception):
    pass


class AbstractFileTree(object):

    def __init__(self, rootdir):
        self.rootdir = rootdir
        if rootdir is not None:
            self.add_root(rootdir)

    def add_file(self, df):
        pass

    def add_files(self, dfs):
        raise NotImplementedError

    def add_root(self, name):
        pass

    def add_experiment(self, exp):
        pass

    def add_dataset(self, dataset, experiment=None):
        pass

    def mapped_file_list(self):
        raise NotImplementedError


class TreeNode(object):
    """
    Holds the data for each node
    """

    def __init__(self, name=None, obj=None, parent=None):
        self.children = {}
        self.obj = obj
        self.name = name
        self.parent = parent
        self._add_obj_fns = {
            Experiment: self.add_experiment,
            Dataset: self.add_dataset,
            DataFile: self.add_datafile,
        }
        self._children = None
        self.auto_children = None

    @property
    def children(self):
        if self._children is None:
            self._children = defaultdict(lambda: TreeNode(self))
        if self.auto_children is not None:
            self._children.update(self.auto_children())
        return self._children

    @children.setter
    def children(self, children):
        self._children = children

    def add_child(self, obj, *args, **kwargs):
        return self._add_obj_fns.get(type(obj), self.add_other)(
            obj, *args, **kwargs)

    def add_other(self, obj):
        if not isinstance(obj, basestring):
            raise NotImplementedError

        path = obj.strip('/')
        base, top = os.path.split(os.path.normpath(path))

        if len(base) > 0:
            parent = self.add_other(base)
        else:
            parent = self
        child = parent.children[top]
        child.name = top
        return child

    def add_experiment(self, exp, auto_update=True):
        directories = getattr(exp, 'directory', '')
        if len(directories) > 0:
            parent = self.add_child(directories)
        else:
            parent = self
        child = parent.children[(Experiment, exp.id)]
        child.obj = exp
        child.name = exp.title
        child.auto_children = child.add_exp_datasets
        return child

    def add_dataset(self, ds):
        raise NotImplementedError

    def add_datafile(self, df):
        raise NotImplementedError

    def add_exp_datasets(self):
        for ds in self.obj.datasets.all():
            self.add_child(ds)


class DefaultFileTree(AbstractFileTree):
    """
    Build a tree from all information available on DataFile, Dataset and
    Experiment records

    E.g.
    Experiment 1/Dataset 1/DataFile 1
    rootdir/exp_sub/dirs/Exp 1/ds_sub/dirs/Dataset 1/df_sub_dirs/Datafile 1

    Trees can be composed from any collection or combination of objects.
    When an object is added, a record of it is kept and it is added to a file
    tree.
    Experiments and Datasets are evaluated lazily.
    """

    def __init__(self, rootdir, ws_to_us=None):
        super(DefaultFileTree, self).__init__(rootdir)

        self.ws_to_us = ws_to_us or getattr(
            settings, 'SPACES_TO_UNDERSCORES', False)

        self.tree = self.TreeNode(name=rootdir, obj=exp)

    def add_experiment(self, exp):
        return self.tree.add_child(exp)

    def add_dataset(self, ds, exp=None):
        exp = exp or ds.experiments.first()
        exp_branch = self.add_experiment(exp)
        return exp_branch.add_child(ds)

    def add_datafile(self, df, exp=None):
        ds_branch = self.add_dataset(df.dataset, exp)
        ds_branch.add_child(df)

    def add_datafiles(self, df_set, exp=None):
        for df in df_set:
            self.add_datafile(df, exp)


    def format_exp(self, exp):
        # if self.experiments
        return exp.title

    def format_ds(self, ds):
        pass

    def format_df(self, df):
        pass

    def mapped_file_list(self):
        pass
        # return self.tree.as_list()

    def sanitise(self, title):
        if self.ws_to_us:
            title = whitespace_to_underscores(title)
        return path_string_escape(title)

    def get_add_experiment(self, exp):
        return self.tree.nodes[exp.id]


class FlatFileTree(AbstractFileTree):
    """
    Ignore folders, only separate Experiments and Datasets
    """

    def mapped_file_list(self):
        pass

    def add_files(self, dfs):
        pass

    def __init__(self):
        super(AbstractFileTree, self).__init__()
        raise NotImplementedError


def map_files_to_paths(datafiles, organization=None, rootdir=None):
    trees = getattr(settings, 'FILE_TREES', {})
    tree_classname = trees.get(organization, None)
    try:
        if tree_classname is not None:
            tree = import_string(tree_classname)(rootdir=rootdir)
        else:
            tree = DefaultFileTree(rootdir=rootdir)
    except ImportError:
        tree = DefaultFileTree(rootdir=rootdir)
    tree.add_files(datafiles)
    return tree.mapped_file_list()


def deep_storage_mapper(obj, rootdir=None):
    """
    File mapper that works for files stored in deep directory structures.
    It recreates the structure as stored in the datafile directory

    :param obj: The model instance (DataFile, Dataset or Experiment)
                to generate a path for.
    :param rootdir: The top-level directory name, or None
    :return: Filesystem-safe path for the object in the archive or SFTP view.

    If rootdir is None, just return a filesystem-safe representation of the
    object, e.g. "DatasetDescription_123" or "strange %2F filename.txt"

    For now, only DataFiles are supported when rootdir is not None.
    """
    if not rootdir:
        if isinstance(obj, DataFile):
            return path_string_escape(obj.filename)
        elif isinstance(obj, Dataset):
            if settings.DATASET_SPACES_TO_UNDERSCORES:
                desc = obj.description.replace(' ', '_')
            else:
                desc = obj.description
            return path_string_escape("%s_%d" % (desc, obj.id))
        elif isinstance(obj, Experiment):
            if getattr(settings, 'EXP_SPACES_TO_UNDERSCORES', False):
                title = obj.title.replace(' ', '_')
            else:
                title = obj.title
            return path_string_escape("%s_%d" % (title, obj.id))
        else:
            raise NotImplementedError(type(obj))

    if not isinstance(obj, DataFile):
        raise NotImplementedError(type(obj))

    datafile = obj
    dataset = datafile.dataset
    exp = dataset.get_first_experiment()
    filepath = os.path.join(dataset.directory or '',
                            path_string_escape(dataset.description),
                            datafile.directory or '', datafile.filename)
    if rootdir != 'datasets':
        return os.path.join(rootdir, filepath)
    elif exp is not None:
        return os.path.join(exp.directory or '', exp.title, filepath)
    else:
        raise Exception


def get_download_organizations():
    trees = getattr(settings, 'FILE_TREES', {})
    return trees.keys()


class DynamicTree(object):

    def __init__(self, host_obj=None):
        self.name = None
        self.obj = None  # an object if applicable
        self.update = self.update_nothing
        self.last_updated = None  # a time.time() number
        self.host_obj = host_obj
        self.children = None
        self.clear_children()

    def update_nothing(self):
        pass

    def clear_children(self):
        self.children = collections.defaultdict(
            lambda: DynamicTree(self.host_obj))

    def add_path(self, path):
        path = path.strip('/')
        elems = split_path(path)
        return self.add_path_elems(elems)

    def add_path_elems(self, elems):
        first = elems[0]
        leaf = self.children[first]
        leaf.name = first
        if len(elems) > 1:
            return leaf.add_path_elems(elems[1:])
        return leaf

    def add_child(self, name, obj=None):
        new_child = self.children[name]
        new_child.name = name
        new_child.obj = obj

    def get_leaf(self, path, update=False):
        path = path.strip('/')
        elems = collections.deque(split_path(path))
        leaf = self.children.get(elems.popleft())
        if leaf and update:
            leaf.update()
        while elems:
            leaf = leaf.children.get(elems.popleft())
            if leaf and update:
                leaf.update()
        return leaf

    def update_experiments(self):
        exps = [(path_mapper(exp), exp)
                for exp in self.host_obj.experiments]
        self.clear_children()
        for exp_name, exp in exps:
            child = self.children[exp_name]
            child.name = exp_name
            child.obj = exp
            child.update = child.update_datasets

    def update_datasets(self):
        all_files_name = '00_all_files'
        datasets = [(path_mapper(ds), ds)
                    for ds in self.obj.datasets.all()]
        self.clear_children()
        for ds_name, ds in datasets:
            if ds_name == all_files_name:
                ds_name = '%s_dataset' % all_files_name
            child = self.children[ds_name]
            child.name = ds_name
            child.obj = ds
            child.update = child.update_dataset_files
        child = self.children[all_files_name]
        child.name = all_files_name
        child.obj = self.obj
        child.update = child.update_all_files

    def update_all_files(self):
        self.clear_children()
        for df in DataFile.objects.filter(
                dataset__experiments=self.obj).iterator():
            self._add_file_entry(df)

    def update_dataset_files(self):
        self.clear_children()
        for df in self.obj.datafile_set.all().iterator():
            self._add_file_entry(df)

    def _add_file_entry(self, datafile):
        df_name = path_mapper(datafile)
        # try:
        #     file_obj = df.file_object
        #     file_name = df_name
        # except IOError:
        #     file_name = df_name + "_offline"
        #     if getattr(settings, 'DEBUG', False):
        #         placeholder = df.file_objects.all()[0].uri
        #     else:
        #         placeholder = 'offline file, contact administrator'
        #     file_obj = StringIO(placeholder)
        # child = self.children[file_name]
        # child.name = file_name
        # child.obj = file_obj

        def add_unique_name(children, orig_name):
            counter = 1
            name = orig_name
            while name in children:
                counter += 1
                name = '%s_%i' % (orig_name, counter)
            return name, children[name]

        if datafile.directory:
            path = self.add_path(datafile.directory)
            df_name, child = add_unique_name(path.children, df_name)
        else:
            df_name, child = add_unique_name(self.children, df_name)
        child.name = df_name
        child.obj = datafile
