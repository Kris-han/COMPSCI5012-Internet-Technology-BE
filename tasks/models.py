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

    class Status(models.IntegerChoices):
        TODO = 1, 'To Do'
        IN_PROGRESS = 2, 'In Progress'
        COMPLETED = 3, 'Completed'
        POSTPONED = 4, 'Postponed'

    class Priority(models.IntegerChoices):
        LOW = 1, 'Low'
        MEDIUM = 2, 'Medium'
        HIGH = 3, 'High'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True) 
    

    status = models.IntegerField(choices=Status.choices, default=Status.TODO)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.MEDIUM)
    due_date = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_tasks')
    executor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='executed_tasks', null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', null=True)

    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    start_time_ts = models.BigIntegerField() # task start time timestamp
    end_time_ts = models.BigIntegerField() # task end time timestamp

    def __str__(self):
        return self.title