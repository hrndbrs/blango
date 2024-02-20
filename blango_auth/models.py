from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _

# Create your models here.
class BlangoUserManager(UserManager):
  def _create_user(self, email, password, **extras):
    if not email:
      raise ValueError("Email is required")
    email = self.normalize_email(email)
    user = self.model(email=email, **extras)
    user.set_password(password)
    user.save(using=self._db)

    return user

  def create_user(self, email, password=None, **extras):
    extras.setdefault("is_staff", False)
    extras.setdefault("is_superuser", False)

    return self._create_user(email, password, **extras)
  
  def create_superuser(self, email, password, **extras):
    extras.setdefault("is_staff", True)
    extras.setdefault("is_superuser", True)
    
    if extras.get("is_staff") is not True:
      raise ValueError("Superuser must have is_staff=True.")
    if extras.get("is_superuser") is not True:
      raise ValueError("Superuser must have is_superuser=True.")
    
    return self._create_user(email, password, **extras)

class User(AbstractUser):
  username = None
  email = models.EmailField(
    _("email address"),
    unique=True,
  )
  objects = BlangoUserManager()

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = []

  def __str__(self):
    return self.email