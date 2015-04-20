from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import DjangoObjectPermissions
from rest_framework.response import Response

from django.contrib.auth.models import User
from django.core.servers.basehttp import FileWrapper
from django.http import StreamingHttpResponse

from tardis.tardis_portal.models import DatafileParameter
from tardis.tardis_portal.models import DatafileParameterSet
from tardis.tardis_portal.models import Dataset
from tardis.tardis_portal.models import DatasetParameter
from tardis.tardis_portal.models import DatasetParameterSet
from tardis.tardis_portal.models import DataFile
from tardis.tardis_portal.models import Experiment
from tardis.tardis_portal.models import ExperimentParameter
from tardis.tardis_portal.models import ExperimentParameterSet
from tardis.tardis_portal.models import ObjectACL
from tardis.tardis_portal.models import ParameterName
from tardis.tardis_portal.models import Schema
from tardis.tardis_portal.models import StorageBox
from tardis.tardis_portal.models import Token

from .serializers import UserSerializer
from .serializers import DatafileParameterSerializer
from .serializers import DatafileParameterSetSerializer
from .serializers import DatasetSerializer
from .serializers import DatasetParameterSerializer
from .serializers import DatasetParameterSetSerializer
from .serializers import DataFileSerializer
from .serializers import ExperimentSerializer
from .serializers import ExperimentParameterSerializer
from .serializers import ExperimentParameterSetSerializer
from .serializers import ObjectACLSerializer
from .serializers import ParameterNameSerializer
from .serializers import SchemaSerializer
from .serializers import StorageBoxSerializer
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

    @detail_route(methods=['post'],
                  permission_classes=[DjangoObjectPermissions])
    def set_storage_box(self, request, pk=None):
        if pk is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        dataset = Dataset.objects.get(id=pk)
        if not request.user.has_perm('tardis_portal.change_dataset',
                                     dataset):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        import ipdb; ipdb.set_trace()


class DatasetParameterViewSet(viewsets.ModelViewSet):
    queryset = DatasetParameter.objects.all()
    serializer_class = DatasetParameterSerializer


class DatasetParameterSetViewSet(viewsets.ModelViewSet):
    queryset = DatasetParameterSet.objects.all()
    serializer_class = DatasetParameterSetSerializer


class DataFileViewSet(viewsets.ModelViewSet):
    queryset = DataFile.objects.all()
    serializer_class = DataFileSerializer

    def get_queryset(self):
        from tardis.tardis_portal.auth.decorators import \
            get_accessible_datafiles_for_user
        return get_accessible_datafiles_for_user(self.request)

    @detail_route(methods=['get'],
                  permission_classes=[DjangoObjectPermissions])
    def download(self, request, pk):
        try:
            datafile = DataFile.objects.get(pk=pk)
        except DataFile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not request.user.has_perm('tardis_acls.view_dataset_file',
                                     datafile):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        file_object = datafile.get_file()
        wrapper = FileWrapper(file_object)
        response = StreamingHttpResponse(
            wrapper, content_type=datafile.mimetype)
        response['Content-Length'] = datafile.size
        response['Content-Disposition'] = 'attachment; filename="%s"' % \
                                          datafile.filename
        response['X-Accel-Buffering'] = 'no'
        return response


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


class SchemaViewSet(viewsets.ModelViewSet):
    queryset = Schema.objects.all()
    serializer_class = SchemaSerializer


class StorageBoxViewSet(viewsets.ModelViewSet):
    queryset = StorageBox.objects.all()
    serializer_class = StorageBoxSerializer


class TokenViewSet(viewsets.ModelViewSet):
    queryset = Token.objects.all()
    serializer_class = TokenSerializer
