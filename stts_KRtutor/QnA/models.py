from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class QuestionAndAnswer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_author")
    title = models.CharField(max_length=100)
    text = models.TextField()
    hit = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return self.author.username

    @property
    def update_counter(self):
        self.hit = self.hit + 1
        self.save()
