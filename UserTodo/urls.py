from django.contrib import admin
from django.urls import path, re_path

from Todo import views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^$', views.home, name='home'),
    re_path(r'^login', views.login, name='login'),
    re_path(r'^signin', views.signin, name='signin'),
    re_path(r'^todos', views.todos, name='todos'),
    re_path(r'^comment', views.comment, name='comment'),
    re_path(r'^add_todo', views.add_todo, name='add_todo'),
    re_path(r'^todo/(?P<todo_id>\d+)/', views.single_todo, name='single_todo'),
    re_path(r'^edit/(?P<todo_id>\d+)', views.edit, name='edit'),
    re_path(r'^delete/(?P<todo_id>\d+)/', views.delete, name='delete'),
]
