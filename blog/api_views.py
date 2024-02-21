import json
from http import HTTPStatus

from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from blog.models import Post
from blog.api.serializers import PostSerializer

# def post_to_dict(post):
#     return {
#         "pk": post.pk,
#         "author_id": post.author_id,
#         "created_at": post.created_at,
#         "modified_at": post.modified_at,
#         "published_at": post.published_at,
#         "title": post.title,
#         "slug": post.slug,
#         "summary": post.summary,
#         "content": post.content,
#     }

@csrf_exempt
def post_list(req, format=None):
  if req.method == "GET":
    # posts = [post_to_dict(post) for post in Post.objects.all()]
    posts = Post.objects.all()
    
    return JsonResponse({"data": PostSerializer(posts, many=True).data})

  elif req.method == "POST":
    post_data = json.loads(req.body)
    # post = Post.objects.create(**post_data)
    s = PostSerializer(data=post_data)
    s.is_valid(raise_exception=True)
    post = s.save()

    return HttpResponse(
      status=HTTPStatus.CREATED,
      headers={"Location": reverse("api_post_detail", args=(post.pk,))}
    )
  
  return HttpResponseNotAllowed(["GET", "POST"])

@csrf_exempt
def post_detail(req, pk, format=None):
  post = get_object_or_404(Post, pk=pk)

  if req.method == "GET":
    # return JsonResponse(post_to_dict(post))
    return JsonResponse(PostSerializer(post).data)

  elif req.method == "PUT":
    post_data = json.loads(req.body)
    # for field, value in post_data.items():
    #   setattr(post, field, value)
    # post.save()

    s = PostSerializer(post, data=post_data)
    s.is_valid(raise_exception=True)
    s.save()

    return HttpResponse(status=HTTPStatus.NO_CONTENT)

  elif req.method == "DELETE":
    post.delete()
    
    return HttpResponse(status=HTTPStatus.NO_CONTENT)

  return HttpResponseNotAllowed(["GET", "PUT", "DELETE"])