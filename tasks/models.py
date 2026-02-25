from django.db import models
from django.contrib.auth.models import User  # 必须引入 Django 自带的用户模型

# 1. 定义 Project 模型
# 为了让 Task 能关联到 Project，我们需要先定义它。
# 既然文件列表里没有看到单独的 project app，我们先在这里定义一个简易版。
class Project(models.Model):
    name = models.CharField(max_length=100)
    # 按照设计文档，Project 也有 user_id，这里简化处理先跑通流程
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project"  # 保持和组长一样的命名风格

    def __str__(self):
        return self.name

# 2. 定义 Task 模型
class Task(models.Model):
    class Meta:
        db_table = "task"  # 保留组长写的表名定义

    # --- 枚举定义 (对应 Design Specification Page 6) ---
    class Status(models.IntegerChoices):
        TODO = 1, 'To Do'
        IN_PROGRESS = 2, 'In Progress'
        COMPLETED = 3, 'Completed'
        POSTPONED = 4, 'Postponed'

    class Priority(models.IntegerChoices):
        LOW = 1, 'Low'
        MEDIUM = 2, 'Medium'
        HIGH = 3, 'High'

    # --- 字段定义 ---
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)  # 允许为空
    
    # 状态和优先级 (使用上面的枚举)
    status = models.IntegerField(choices=Status.choices, default=Status.TODO)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.MEDIUM)
    
    # 截止日期
    due_date = models.DateTimeField(null=True, blank=True)
    
    # --- 外键关联 (最重要的一步) ---
    # owner: 任务拥有者 (关联 User 表)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_tasks')
    
    # executor: 执行者 (可以为空，如果没指派人的话)
    executor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='executed_tasks', null=True)
    
    # project: 所属项目 (关联上面的 Project 表)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', null=True)

    # --- 时间字段 ---
    # 根据文档将 created_at 改为 create_time，或者你可以改回 created_at，这里我遵循文档
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title