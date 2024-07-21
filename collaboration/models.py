# collaboration/models.py
from django.db import models
from django.contrib.auth.models import User

class Document(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    owner = models.ForeignKey(User, related_name='owned_documents', on_delete=models.CASCADE)
    shared_with = models.ManyToManyField(User, related_name='shared_documents')

class Permission(models.Model):
    document = models.ForeignKey(Document, related_name='permissions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='collaborations', on_delete=models.CASCADE)
    can_edit = models.BooleanField(default=False)
