from rest_framework import serializers
from blog.models import Post
import time
from django.utils.text import slugify

class PostSerializer(serializers.ModelSerializer):
  slug = serializers.SlugField(required=False)

  class Meta:
    model = Post
    fields = "__all__"
    readonly = ["modified_at", "created_at"]

  def validate(self, data):
    data["slug"] = slugify(f"{data['title']}-{int(time.time() * 1000)}")

    return data
    
    