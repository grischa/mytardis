import string

import datetime
from hypothesis.extra.django.models import models
from hypothesis.strategies import lists, just, text

from django.contrib.auth.models import User
from django.test import Client, TestCase

from tardis.tardis_portal.models import Dataset, Experiment


class ExperimentListingViewTestCase(TestCase):

    def setUp(self):
        ascii_text = list(string.ascii_letters + string.digits)
        self.password = text(alphabet=ascii_text).example()
        self.username = text(alphabet=ascii_text).example()
        self.user = User(username=self.username)
        self.user.set_password(self.password)
        self.user.save()
        self.client = Client()
        logged_in = self.client.login(username=self.user.username,
                                      password=self.password)
        self.assertTrue(logged_in)
        self.experiments = lists(models(Experiment, created_by=just(self.user)),
                                 min_size=100, max_size=200)
        self.experiment = models(
            Experiment, created_by=just(self.user)).example()

    def test_experiment_list(self):

        self.assertEqual(self.experiment.created_by.username,
                         self.user.username)

    def test_mydata_page_timing(self):
        start = datetime.datetime.now()
        mydata_page = self.client.get('/mydata/')
        duration = datetime.datetime.now() - start
        self.assertEqual(mydata_page.status_code, 200)
        self.assertLess(duration.total_seconds(), 2)
