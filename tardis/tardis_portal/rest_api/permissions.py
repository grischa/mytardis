from rest_framework import permissions

from django.contrib.contenttypes.models import ContentType


class MyTardisPermissions(permissions.BasePermission):
    app_label = 'tardis_acls'

    def has_permission(self, request, view):
        safe = request.method in permissions.SAFE_METHODS
        return safe or request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            verb = 'view'
        elif request.method in ('DELETE',):
            verb = 'delete'
        else:
            verb = 'change'
        ct = ContentType.objects.get_for_model(obj)
        permission = '%s.%s_%s' % (self.app_label,
                                   verb, ct.model)
        return request.user.has_perm(permission, obj)
