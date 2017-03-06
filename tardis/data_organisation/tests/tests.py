"""
Unit tests for file mapping
"""
from django.contrib.auth.models import User
from django.test import TestCase

from tardis.data_organisation.mapping_to_paths import TreeNode
from tardis.tardis_portal.models import Dataset
from tardis.tardis_portal.models import Experiment


class FileMappingTestCase(TestCase):

    def setUp(self):
        testuser = User(username='testuser')
        testuser.save()
        self.exp = Experiment(title='tree tests',
                              created_by=testuser)
        self.exp.save()
        self.dataset = self.exp.datasets.create(description='test dataset')

    def testAddFilePathToTree(self):
        tree = TreeNode()
        tree.add_child('/some/path')
        self.assertIn('some', tree.children)
        self.assertIn('path', tree.children['some'].children)

    def testAddExpToTree(self):
        tree = TreeNode()
        tree.add_child(self.exp)
        self.assertIn((Experiment, self.exp.id), tree.children)
        self.assertEqual(self.exp.title,
                         tree.children[(Experiment, self.exp.id)].name)
        self.assertEqual(self.exp,
                         tree.children[(Experiment, self.exp.id)].obj)
        # auto-update
        self.assertIn((Dataset, self.dataset.id),
                      tree.children[self.exp.id].children)
