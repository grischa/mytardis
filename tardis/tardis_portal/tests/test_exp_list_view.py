import string

import datetime

from django.db import transaction
from hypothesis import given, settings
from hypothesis.extra.django.models import models
from hypothesis.strategies import lists, just, text, data, integers

from django.contrib.auth.models import User
from django.test import Client, TestCase

from tardis.tardis_portal.models import (Dataset, Experiment, ExperimentAuthor,
                                         DataFile)

# some constants
exp_num = 8
ds_per_exp = 6
time_limit = 4.0


# set up hypothesis generators (data is not being created)
def experiments(user):
    # self.experiments = lists(models(Experiment, created_by=just(self.user)),
    #                          min_size=exp_num, max_size=exp_num)
    datasets = lists(models(Dataset),
                     min_size=exp_num * ds_per_exp,
                     max_size=exp_num * ds_per_exp)
    for i in range(exp_num):
        lists(models(Dataset), min_size=ds_per_exp,
              max_size=ds_per_exp).map(lambda ds: ds.experiments.add(
              models(Experiment, created_by=just(user)).example()
        ))
        # self.experiments.flatmap(lambda x: x)
        #     # for ds in self.datasets[ds_per_exp * i:ds_per_exp * (i + 1)]:
        #     #     e.dataset.add(ds)
        # self.experiment = models(
        #     Experiment, created_by=just(self.user)).example()
    return datasets


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

    @given(data())
    @settings(max_examples=1, timeout=120)
    def test_experiment_list(self, d):
        # import ipdb; ipdb.set_trace()
        exps = d.draw(lists(models(
            Experiment,
            created_by=just(self.user)),
            min_size=exp_num,
            max_size=exp_num))
        datasets = d.draw(lists(models(Dataset), min_size=ds_per_exp * exp_num,
                                max_size=ds_per_exp * exp_num))
        for i, e in enumerate(exps):
            for ds in datasets[i * ds_per_exp:(i + 1) * ds_per_exp]:
                ds.experiments.add(e)
            d.draw(lists(models(ExperimentAuthor, experiment=just(e)),
                         min_size=2, max_size=5))
        for ds in datasets:
            dfs = d.draw(lists(models(DataFile, dataset=just(ds),
                                      size=integers(min_value=0),
                                      md5sum=text(
                                          min_size=32, max_size=32),
                                      mimetype=just('image/jpeg')),
                               min_size=3, max_size=5))
        self.assertEqual(len(exps), exp_num)
        self.assertEqual(len(datasets), exp_num * ds_per_exp)

    def test_mydata_page_timing(self):
        start = datetime.datetime.now()
        mydata_page = self.client.get('/mydata/')
        duration = datetime.datetime.now() - start
        self.assertEqual(mydata_page.status_code, 200)
        self.assertLess(duration.total_seconds(), time_limit)
