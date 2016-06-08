from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'UserTodo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'Todo.views.home', name='home'),
    url(r'^login', 'Todo.views.login', name='login'),
    url(r'^signin', 'Todo.views.signin', name='signin'),
    url(r'^todos', 'Todo.views.todos', name='todos'),
    url(r'^comment', 'Todo.views.comment', name='comment'),
    url(r'^add_todo', 'Todo.views.add_todo', name='add_todo'),
    url(r'^todo/(?P<todo_id>\d+)/', 'Todo.views.single_todo', name='single_todo'),
    url(r'^edit/(?P<todo_id>\d+)', 'Todo.views.edit', name='edit'),
    url(r'^delete/(?P<todo_id>\d+)/', 'Todo.views.delete', name='delete'),
]
