from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie

from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from blog.api.serializers import (
    PostSerializer,
    UserSerializer,
    PostDetailSerializer,
    TagSerializer,
)
from rest_framework.exceptions import PermissionDenied

from blog.api.permissions import AuthorModifyOrReadOnly, IsAdminUserForObject
from blog.models import Post, Tag
from blango_auth.models import User

"""
Leaving it here for learning purposes

class PostList(generics.ListCreateAPIView):
  queryset = Post.objects.all()
  serializer_class = PostSerializer

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
  permission_classes = [AuthorModifyOrReadOnly | IsAdminUserForObject]
  queryset = Post.objects.all()
  serializer_class = PostDetailSerializer
"""

class UserDetail(generics.RetrieveAPIView):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  lookup_field = "email"

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    @action(methods=["get"], detail=True, name="Posts with the tag")
    def posts(self, req, pk=None):
      tag = self.get_object()
      post_serializer = PostSerializer(
        tag.posts, many=True, context = {"request": req}
      )

      return Response(post_serializer.data)

    @method_decorator(cache_page(300))
    def list(self, *args, **kwargs):
        return super(TagViewSet, self).list(*args, **kwargs)

    @method_decorator(cache_page(300))
    def retrieve(self, *args, **kwargs):
        return super(TagViewSet, self).retrieve(*args, **kwargs)



class PostViewSet(viewsets.ModelViewSet):
  permission_classes = [AuthorModifyOrReadOnly|IsAdminUserForObject]
  queryset = Post.objects.all()

  def get_serializer_class(self):
    if self.action in ("list", "create"):
      return PostSerializer
    return PostDetailSerializer

  @method_decorator(cache_page(300))
  @method_decorator(vary_on_headers("Authorization"))
  @method_decorator(vary_on_cookie)
  @action(methods=["get"], detail=False, name="Posts by the logged in user")
  def mine(self, req):
    if(req.user.is_anonymous):
      raise PermissionDenied("You must be logged in to see which Posts are yours")
    posts = self.get_queryset().filter(author=req.user)
    serializer = PostSerializer(posts, many=True, context={"request": req})
    return Response(serializer.data)

  @method_decorator(cache_page(120))
  def list(self, *args, **kwargs):
    return super(PostSerializer, self).list(*args, **kwargs)

  @method_decorator(cache_page(120))
  def get(self, *args, **kwargs):
    return super(PostSerializer, self).get(*args, **kwargs)