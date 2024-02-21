from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from blog.api.views import PostDetail, PostList

urlpatterns = format_suffix_patterns([
  path("posts/", PostList.as_view(), name="api_post_list"),
  path("posts/<int:pk>/", PostDetail.as_view(), name="api_post_detail")
])