import random
import string

import datetime

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from hypothesis import given, settings
from hypothesis.extra.django.models import models
from hypothesis.strategies import lists, just, text, data, integers

from django.contrib.auth.models import User
from django.test import Client, TestCase

from tardis.tardis_portal.models import (Dataset, Experiment, ExperimentAuthor,
                                         DataFile, ObjectACL)

# some constants
exp_num = 50
authors_per_exp = 6
ds_per_exp = 30
files_per_ds = 50
time_limit = 3.5


class ExperimentListingViewTestCase(TestCase):

    def setUp(self):
        ascii_text = list(string.ascii_letters + string.digits)
        self.password = text(alphabet=ascii_text).example()
        self.username = text(alphabet=ascii_text).example()
        try:
            self.user = User.objects.get(username=self.username)
        except User.DoesNotExist:
            self.user = User(username=self.username)
        self.user.set_password(self.password)
        self.user.save()
        self.client = Client()
        logged_in = self.client.login(username=self.user.username,
                                      password=self.password)
        self.assertTrue(logged_in)
        new_exps = []
        for i in range(exp_num):
            desc = text().example()
            new_exps.append(Experiment(description=desc,
                                       created_by=self.user))
        Experiment.objects.bulk_create(new_exps)
        new_dss = []
        for i in range(exp_num * ds_per_exp):
            new_dss.append(Dataset(description=text().example()))
        Dataset.objects.bulk_create(new_dss)
        authors = []
        author_names = lists(text(), min_size=authors_per_exp,
                             max_size=authors_per_exp, unique=True).example()
        oacls = []
        for i, e in enumerate(Experiment.objects.all().iterator()):
            for ds in Dataset.objects.all()[
                      i * ds_per_exp:(i + 1) * ds_per_exp]:
                ds.experiments.add(e)
            for j, a in enumerate(author_names):
                authors.append(ExperimentAuthor(experiment=e,
                                                author=a,
                                                order=j))
            oacls.append(ObjectACL(
                pluginId ='django_user',
                entityId=self.user.id,
                content_type=ContentType.objects.get_for_model(Experiment),
                object_id=e.id,
                canRead=True,
                canWrite=True,
                isOwner=random.choice([True, False])
            ))
        ObjectACL.objects.bulk_create(oacls)
        ExperimentAuthor.objects.bulk_create(authors)
        datafiles = []
        for ds in Dataset.objects.all().iterator():
            for i in range(files_per_ds):
                datafiles.append(DataFile(
                    filename="testfile.test",
                    dataset=ds,
                    size=12345,
                    md5sum="123456789abcdef0123456789abcdef" * 2,
                    mimetype=random.choice(['text/plain', 'image/jpeg'])))
        DataFile.objects.bulk_create(datafiles)

    def test_mydata_page_timing(self):
        self.assertEqual(Experiment.objects.all().count(), exp_num)
        self.assertEqual(Dataset.objects.all().count(), exp_num * ds_per_exp)
        self.assertEqual(DataFile.objects.all().count(),
                         exp_num * ds_per_exp * files_per_ds)

        start = datetime.datetime.now()
        mydata_page = self.client.get('/mydata/')
        duration = datetime.datetime.now() - start
        self.assertEqual(mydata_page.status_code, 200)
        self.assertLess(duration.total_seconds(), time_limit)
