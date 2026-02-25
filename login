from django.db import models
from django.contrib.auth.models import AbstractUser
class UserProfile(AbstractUser):
    """
    自定义用户模型：支持登录、注册以及额外的个人信息
    """
    # 扩展字段
    phone_number = models.CharField(max_length=11, unique=True, verbose_name="手机号", null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="头像")
    nickname = models.CharField(max_length=50, blank=True, verbose_name="昵称")
class Gender(models.IntegerChoices):
        UNKNOWN = 0, '保密'
        MALE = 1, '男'
        FEMALE = 2, '女'
gender = models.IntegerField(choices=Gender.choices, default=Gender.UNKNOWN, verbose_name="性别")
class Meta:
        db_table = "user_profile" # 保持和你之前代码统一的命名风格
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
