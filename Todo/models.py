from django.db import models
# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s" % (self.name)


class Todo(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User)
    description = models.CharField(max_length=200)
    is_deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s" % (self.name)


class Comment(models.Model):
    todo = models.ForeignKey(Todo)
    description = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s" % (self.todo.name)
