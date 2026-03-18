import secrets
from django.db import models


class User(models.Model):
    class Meta:
        db_table = "user"
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
            models.Index(fields=["is_active"]),
        ]

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    avatar = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} <{self.email}>"




class UserToken(models.Model):
    class Meta:
        db_table = "user_token"
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["user_id"]),
        ]

    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="tokens")
    token = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_token():
        return secrets.token_hex(32)