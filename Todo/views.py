import json

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from Todo.forms import LoginForm
from Todo.models import User, Todo, Comment
# Create your views here.


def home(request):
    request.session['User'] = None
    template = "login.html"
    form = LoginForm()
    return render(request, template, {'loginForm': form})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = User.objects.filter(name=form.data.get('name')).first()
            if user and user.password == form.data.get('password'):
                request.session['User'] = form.data.get('name')
                return redirect('todos')
            else:
                return redirect('home')
    else:
        return redirect('home')


def todos(request):
    if request.session.get('User') is not None:
        template = "todos.html"
        user = User.objects.filter(name=request.session.get('User')).first()
        todos = Todo.objects.filter(user=user.id, is_deleted=False)
        todos_list = list()
        for todo in todos:
            comments = Comment.objects.filter(todo=todo.id)
            single_todo = dict()
            single_todo['id'] = todo.id
            single_todo['name'] = todo.name
            single_todo['description'] = todo.description
            single_todo['comments'] = comments
            todos_list.append(single_todo)
        return render(request, template, {'todos': todos_list})
    else:
        return redirect('home')


def signin(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            form.save()
            request.session['User'] = form.data.get('name')
            return redirect('todos')
    else:
        return redirect('home')


def comment(request):
    if request.session.get('User') is not None:
        print request.session.get('User')
        return HttpResponse("Sucess")


def single_todo(request, todo_id):
    todo = Todo.objects.get(pk=todo_id)
    single_todo = dict()
    single_todo['id'] = todo.id
    single_todo['name'] = todo.name
    single_todo['description'] = todo.description
    return HttpResponse(json.dumps(single_todo))


@csrf_exempt
def edit(request, todo_id):
    if request.session.get('User') and request.is_ajax():
        single_todo = dict()
        todo = Todo.objects.get(pk=todo_id)
        single_todo['prev_name'] = todo.name
        todo.name = request.POST.get('todo_name')
        todo.description = request.POST.get('todo_description')
        todo.save()
        single_todo['id'] = todo.id
        single_todo['name'] = todo.name
        single_todo['description'] = todo.description
        return HttpResponse(json.dumps(single_todo))


def delete(request, todo_id):
    if request.session.get('User') and request.is_ajax():
        todo = Todo.objects.get(pk=todo_id)
        todo.is_deleted = True
        todo.save()
        single_todo = dict()
        single_todo['id'] = todo.id
        single_todo['name'] = todo.name
        single_todo['description'] = todo.description
        return HttpResponse(json.dumps(single_todo))


@csrf_exempt
def add_todo(request):
    if request.session.get('User') is not None:
        user = User.objects.filter(name=request.session.get('User')).first()
        todo = Todo()
        todo.name = request.POST.get('todo_name')
        todo.description = request.POST.get('todo_description')
        todo.user = user
        todo.save()
        return redirect('todos')
