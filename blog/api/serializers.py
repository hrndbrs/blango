from rest_framework import serializers
from blog.models import Post, Tag
from blango_auth.models import User
import time
from django.utils.text import slugify
from blog.models import Post, Tag, Comment

class TagField(serializers.SlugRelatedField):
  def to_internal_value(self, data):
    try:
      return self.get_queryset().get_or_create(value=data.lower())[0]
    except (TypeError, ValueError):
      self.fail(f"Tag balue {data} is invalid")

class PostSerializer(serializers.ModelSerializer):
  slug = serializers.SlugField(required=False)
  tags = serializers.SlugRelatedField(
    slug_field="value", many=True, queryset=Tag.objects.all()
  )
  author = serializers.HyperlinkedRelatedField(
    queryset=User.objects.all(), view_name="api_user_detail", lookup_field="email"
  )
  class Meta:
    model = Post
    fields = "__all__"
    readonly = ["modified_at", "created_at"]

  def validate(self, data):
    data["slug"] = slugify(f"{data['title']}-{int(time.time() * 1000)}")

    return data

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ["first_name", "last_name", "email"]

class CommentSerializer(serializers.ModelSerializer):
  id = serializers.IntegerField(required=False)
  creator = UserSerializer(read_only=True)

  class Meta:
    model = Comment
    fields = ["id", "creator", "content", "modified_at", "created_at"]
    readonly = ["modified_at", "created_at"]

class PostDetailSerializer(PostSerializer):
  comments = CommentSerializer(many=True)

  def update(self, instance, validated_data):
    comments = validated_data.pop("comments")
    instance = super(PostDetailSerializer, self).update(instance, validated_data)

    for comment_data in comments:
      if comment_data.get("id"):
        continue
      
      comment = Comment(**comment_data)
      comment.creator = self.context["request"].User
      comment.content_object = instance
      comment.save()

    return instance
    