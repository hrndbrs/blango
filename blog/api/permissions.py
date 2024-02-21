from rest_framework import permissions

class AuthorModifyOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
  def has_object_permission(self, req, view, obj):
    if req.method in permissions.SAFE_METHODS:
      return True
    
    return request.user == obj.author

class IsAdminUserForObject(permissions.IsAdminUser):
  def has_object_permission(self, req, view, obj):
    return bool(req.user and req.user.is_staff)

    