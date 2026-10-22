from django.contrib.auth.hashers import check_password, make_password
from django.db import models
# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=100)
    # Stores a Django password hash (never the plain-text password).
    password = models.CharField(max_length=128)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        def upgrade(raw):
            self.set_password(raw)
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, upgrade)

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
