from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie
from django.db.models import Q
from django.http import Http404

from datetime import timedelta

from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from blog.api.serializers import (
    PostSerializer,
    UserSerializer,
    PostDetailSerializer,
    TagSerializer,
)
from blog.api.permissions import AuthorModifyOrReadOnly, IsAdminUserForObject
from blog.api.filters import PostFilterSet
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
        page = self.paginate_queryset(tag.posts.all())
        if page is not None:
            post_serializer = PostSerializer(
                page, many=True, context={"request": req}
            )
            return self.get_paginated_response(post_serializer.data)
        post_serializer = PostSerializer(
            tag.posts, many=True, context={"request": req}
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
  filterset_class = PostFilterSet
  ordering_fields = ["published_at", "author", "title", "slug"]
  
  # filterset_fields = ["author", "tags"] 
  # setting fields to filter from using base filter class set in settings.py
  
  def get_serializer_class(self):
    if self.action in ("list", "create"):
      return PostSerializer
    return PostDetailSerializer

  def get_queryset(self):

    if self.request.user.is_anonymous:
      queryset = self.queryset.filter(published_at__lte=timezone.now())
    elif self.request.user.is_staff:
      queryset = self.queryset
    else:
      queryset = self.queryset.filter(
        Q(published_at__lte=timezone.now()) | Q(author=self.request.user)
      )
    time_period_name = self.kwargs.get("period_name")

    if not time_period_name:
      return queryset
    elif time_period_name == "new":
      return queryset.filter(
        published_at__gte=timezone.now().date() - timedelta(hours=1)
      )
    elif time_period_name == "today":
      return queryset.filter(
        published_at__date=timezone.now().date()
      )
    elif time_period_name == "week":
      return queryset.filter(
        published_at__gte=timezone.now().date() - timedelta(days=7)
      )
    else: 
      raise Http404(
        f"Time period {time_period_name} is not valid, should be "
        f"'new', 'today' or 'week'"
      )

  @method_decorator(cache_page(300))
  @method_decorator(vary_on_headers("Authorization"))
  @method_decorator(vary_on_cookie)
  @action(methods=["get"], detail=False, name="Posts by the logged in user")
  def mine(self, req):
    if(req.user.is_anonymous):
      raise PermissionDenied("You must be logged in to see which Posts are yours")

    posts = self.get_queryset().filter(author=req.user)

    page = self.paginate_queryset(posts)

    if page is not None:
      serializer = PostSerializer(page, many=True, context={"request": req})
      return self.get_paginated_response(serializer.data)

    serializer = PostSerializer(posts, many=True, context={"request": req})
    return Response(serializer.data)

  @method_decorator(cache_page(120))
  @method_decorator(vary_on_headers("Authorization", "Cookie"))
  def list(self, *args, **kwargs):
    return super(PostViewSet, self).list(*args, **kwargs)

  @method_decorator(cache_page(120))
  def get(self, *args, **kwargs):
    return super(PostViewSet, self).get(*args, **kwargs)