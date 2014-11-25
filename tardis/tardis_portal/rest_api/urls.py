from rest_framework import routers

from django.conf.urls import patterns, url, include

from . import views

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'datafile_parameter', views.DatafileParameterViewSet)
router.register(r'datafile_paramter_set', views.DatafileParameterSetViewSet)
router.register(r'dataset', views.DatasetViewSet)
router.register(r'dataset_parameter', views.DatasetParameterViewSet)
router.register(r'dataset_parameter_set', views.DatasetParameterSetViewSet)
router.register(r'datafile', views.DataFileViewSet)
router.register(r'experiment', views.ExperimentViewSet)
router.register(r'experiment_parameter', views.ExperimentParameterViewSet)
router.register(r'experiment_parameter_set',
                views.ExperimentParameterSetViewSet)
router.register(r'object_acl', views.ObjectACLViewSet)
router.register(r'parameter_name', views.ParameterNameViewSet)
router.register(r'schema', views.SchemaViewSet)
router.register(r'storage_box', views.StorageBoxViewSet)
router.register(r'token', views.TokenViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
rest_api_urls = patterns(
    '',
    url(r'^', include(router.urls)),
    # url(r'^api-auth/', include('rest_framework.urls',
    #                            namespace='rest_framework')),
)
