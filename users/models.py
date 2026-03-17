import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):

    # 覆盖 email 字段，确保唯一
    email = models.EmailField(unique=True, verbose_name='Email')

    # 新增字段
    phone_number = models.CharField(
        max_length=11,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Phone Number'
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='Avatar'
    )
    nickname = models.CharField(max_length=50, blank=True, verbose_name='Nickname')
    GENDER_CHOICES = (
        (0, 'Secret'),
        (1, 'Male'),
        (2, 'Female'),
    )
    gender = models.IntegerField(choices=GENDER_CHOICES, default=0, verbose_name='Gender')
    last_login_ip = models.CharField(max_length=50, blank=True, null=True, verbose_name='Last Login IP')
    user_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='User UUID')

    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username
# Create your models here.
