from django.db import models
# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return "%s" % (self.name)


class Todo(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % (self.name)


class Comment(models.Model):
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)

    def __str__(self):
        return "%s" % (self.todo.name)
