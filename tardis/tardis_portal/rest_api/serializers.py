'''
Serializers for RESTful API
In here all API-accessible models have their serializers defined.
'''
from rest_framework import serializers
from rest_framework.relations import HyperlinkedIdentityField

from django.contrib.auth.models import User

from tardis.tardis_portal.models import DatafileParameter
from tardis.tardis_portal.models import DatafileParameterSet
from tardis.tardis_portal.models import Dataset
from tardis.tardis_portal.models import DatasetParameter
from tardis.tardis_portal.models import DatasetParameterSet
from tardis.tardis_portal.models import Dataset_File
from tardis.tardis_portal.models import Experiment
from tardis.tardis_portal.models import ExperimentParameter
from tardis.tardis_portal.models import ExperimentParameterSet
from tardis.tardis_portal.models import ObjectACL
from tardis.tardis_portal.models import ParameterName
from tardis.tardis_portal.models import Replica
from tardis.tardis_portal.models import Schema
from tardis.tardis_portal.models import Token


class RenamedURLHyperlinkedModelSerializer(
        serializers.HyperlinkedModelSerializer):
    '''
    provides a hyperlinked API even though most models already contain a
    url field which prevents that by default
    '''
    api_uri_name = 'uri'

    def get_default_fields(self):
        fields = super(RenamedURLHyperlinkedModelSerializer, self)\
            .get_default_fields()

        uri_field = HyperlinkedIdentityField(
            view_name=self.opts.view_name,
            lookup_field=self.opts.lookup_field
        )
        ret = self._dict_class()
        ret[self.api_uri_name] = uri_field
        ret.update(fields)
        fields = ret
        return fields


class UserSerializer(RenamedURLHyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email')


class DatafileParameterSerializer(RenamedURLHyperlinkedModelSerializer):
    class Meta:
        model = DatafileParameter


class DatafileParameterSetSerializer(RenamedURLHyperlinkedModelSerializer):
    class Meta:
        model = DatafileParameterSet


class DatasetSerializer(RenamedURLHyperlinkedModelSerializer):
    class Meta:
        model = Dataset


class DatasetParameterSerializer(RenamedURLHyperlinkedModelSerializer):
    class Meta:
        model = DatasetParameter


class DatasetParameterSetSerializer(RenamedURLHyperlinkedModelSerializer):
    class Meta:
        model = DatasetParameterSet


class Dataset_FileSerializer(RenamedURLHyperlinkedModelSerializer):
    class Meta:
        model = Dataset_File


class ExperimentSerializer(RenamedURLHyperlinkedModelSerializer):
    class Meta:
        model = Experiment
        fields = ('uri', 'url',
                  # 'approved',
                  'title',
                  'institution_name', 'description',
                  # 'start_time', 'end_time',
                  # 'created_time', 'update_time',
                  # 'created_by', 'handle',
                  # 'locked', 'public_access',
                  # 'license',
                  )


class ExperimentParameterSerializer(RenamedURLHyperlinkedModelSerializer):
    class Meta:
        model = ExperimentParameter


class ExperimentParameterSetSerializer(RenamedURLHyperlinkedModelSerializer):
    class Meta:
        model = ExperimentParameterSet


class ObjectACLSerializer(RenamedURLHyperlinkedModelSerializer):
    class Meta:
        model = ObjectACL


class ParameterNameSerializer(RenamedURLHyperlinkedModelSerializer):
    class Meta:
        model = ParameterName


class ReplicaSerializer(RenamedURLHyperlinkedModelSerializer):
    class Meta:
        model = Replica


class SchemaSerializer(RenamedURLHyperlinkedModelSerializer):
    class Meta:
        model = Schema


class TokenSerializer(RenamedURLHyperlinkedModelSerializer):
    class Meta:
        model = Token
