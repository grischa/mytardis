from rest_framework import viewsets

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

from .serializers import UserSerializer
from .serializers import DatafileParameterSerializer
from .serializers import DatafileParameterSetSerializer
from .serializers import DatasetSerializer
from .serializers import DatasetParameterSerializer
from .serializers import DatasetParameterSetSerializer
from .serializers import Dataset_FileSerializer
from .serializers import ExperimentSerializer
from .serializers import ExperimentParameterSerializer
from .serializers import ExperimentParameterSetSerializer
from .serializers import ObjectACLSerializer
from .serializers import ParameterNameSerializer
from .serializers import ReplicaSerializer
from .serializers import SchemaSerializer
from .serializers import TokenSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class DatafileParameterViewSet(viewsets.ModelViewSet):
    queryset = DatafileParameter.objects.all()
    serializer_class = DatafileParameterSerializer


class DatafileParameterSetViewSet(viewsets.ModelViewSet):
    queryset = DatafileParameterSet.objects.all()
    serializer_class = DatafileParameterSetSerializer


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer


class DatasetParameterViewSet(viewsets.ModelViewSet):
    queryset = DatasetParameter.objects.all()
    serializer_class = DatasetParameterSerializer


class DatasetParameterSetViewSet(viewsets.ModelViewSet):
    queryset = DatasetParameterSet.objects.all()
    serializer_class = DatasetParameterSetSerializer


class Dataset_FileViewSet(viewsets.ModelViewSet):
    queryset = Dataset_File.objects.all()
    serializer_class = Dataset_FileSerializer

    def get_queryset(self):
        from tardis.tardis_portal.auth.decorators import \
            get_accessible_datafiles_for_user
        return get_accessible_datafiles_for_user(self.request)


class ExperimentViewSet(viewsets.ModelViewSet):
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer

    def get_queryset(self):
        '''
        return only allowed experiments
        '''
        return Experiment.safe.all(self.request.user)


class ExperimentParameterViewSet(viewsets.ModelViewSet):
    queryset = ExperimentParameter.objects.all()
    serializer_class = ExperimentParameterSerializer


class ExperimentParameterSetViewSet(viewsets.ModelViewSet):
    queryset = ExperimentParameterSet.objects.all()
    serializer_class = ExperimentParameterSetSerializer


class ObjectACLViewSet(viewsets.ModelViewSet):
    queryset = ObjectACL.objects.all()
    serializer_class = ObjectACLSerializer


class ParameterNameViewSet(viewsets.ModelViewSet):
    queryset = ParameterName.objects.all()
    serializer_class = ParameterNameSerializer


class ReplicaViewSet(viewsets.ModelViewSet):
    queryset = Replica.objects.all()
    serializer_class = ReplicaSerializer


class SchemaViewSet(viewsets.ModelViewSet):
    queryset = Schema.objects.all()
    serializer_class = SchemaSerializer


class TokenViewSet(viewsets.ModelViewSet):
    queryset = Token.objects.all()
    serializer_class = TokenSerializer
