from django.db import models


class Task(models.Model):
    class Meta:
        db_table = "task"

    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)


