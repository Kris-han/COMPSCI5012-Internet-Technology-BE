from django.db import models
from django.contrib.auth.models import User  

class Project(models.Model):
    name = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project" 
 
    def __str__(self):
        return self.name


class Task(models.Model):
    class Meta:
        db_table = "task"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["uid", "status"]),
            models.Index(fields=["uid", "start_time_ts"]),
            models.Index(fields=["uid", "end_time_ts"]),
            models.Index(fields=["uid", "completed_at_ts"]),
        ]

    class Status(models.IntegerChoices):
        TODO = 1, "To Do"
        IN_PROGRESS = 2, "In Progress"
        COMPLETED = 3, "Completed"
        POSTPONED = 4, "Postponed"

    class Priority(models.IntegerChoices):
        LOW = 1, "Low"
        MEDIUM = 2, "Medium"
        HIGH = 3, "High"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    uid = models.BigIntegerField(db_index=True)
    status = models.IntegerField(
        choices=Status.choices,
        default=Status.TODO
    )
    priority = models.IntegerField(
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    start_time_ts = models.BigIntegerField()
    end_time_ts = models.BigIntegerField()
    completed_at_ts = models.BigIntegerField(null=True, blank=True)
    project_name = models.CharField(max_length=200, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.IntegerField(default=0)

    def __str__(self):
        return self.title