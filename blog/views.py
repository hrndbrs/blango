import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from blog.models import Post
from blog.forms import CommentForm

# from django.views.decorators.vary import vary_on_cookie
# from django.views.decorators.cache import cache_page

# Create your views here.
"""
See which IP address that is connected to django

def get_ip(request):
  from django.http import HttpResponse
  return HttpResponse(request.META['REMOTE_ADDR'])
"""

logger = logging.getLogger(__name__)

# @cache_page(300) # Time in seconds
# @vary_on_cookie
def index(req):
  posts = Post.objects.filter(published_at__lte=timezone.now()).select_related("author")

  logger.debug("Got %d posts", len(posts)) 

  return render(req, "blog/index.html", { "posts" : posts })

def post_detail(req, slug):
  post = get_object_or_404(Post, slug=slug)
  
  if req.user.is_active:
    if req.method == "POST":
      comment_form = CommentForm(req.POST)

      if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.content_object = post
        comment.creator = req.user
        comment.save()

        logger.info(
          "Created comment on Post %d for user %s", post.pk, req.user
        )

        
        return redirect(req.path_info)
    else:
      comment_form = CommentForm()
  else:
    comment_form = None
  return render(req, "blog/post-detail.html", {"post": post, "comment_form": comment_form})