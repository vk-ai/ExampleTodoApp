import json

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.views.decorators.http import require_POST

from Todo.forms import LoginForm
from Todo.models import User, Todo, Comment


def _is_ajax(request):
    # HttpRequest.is_ajax() was removed in Django 4.0; jQuery sends this header.
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def _current_user(request):
    name = request.session.get('User')
    if not name:
        return None
    return User.objects.filter(name=name).first()


def _own_todo(request, todo_id):
    """Return the caller's todo, or None if not logged in / not theirs."""
    user = _current_user(request)
    if user is None:
        return None
    return Todo.objects.filter(pk=todo_id, user=user).first()


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
            if user and user.check_password(form.data.get('password')):
                request.session.cycle_key()  # prevent session fixation
                request.session['User'] = user.name
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
            if User.objects.filter(name=form.cleaned_data['name']).exists():
                # Names identify sessions; never create a second account with the same name.
                return redirect('home')
            user = form.save()
            request.session.cycle_key()
            request.session['User'] = user.name
            return redirect('todos')
    else:
        return redirect('home')


def comment(request):
    if request.session.get('User') is not None:
        print(request.session.get('User'))
        return HttpResponse("Sucess")


def single_todo(request, todo_id):
    todo = _own_todo(request, todo_id)
    if todo is None:
        return HttpResponseNotFound()
    single_todo = dict()
    single_todo['id'] = todo.id
    single_todo['name'] = todo.name
    single_todo['description'] = todo.description
    return HttpResponse(json.dumps(single_todo))


@require_POST
def edit(request, todo_id):
    if request.session.get('User') and _is_ajax(request):
        single_todo = dict()
        todo = _own_todo(request, todo_id)
        if todo is None:
            return HttpResponseNotFound()
        single_todo['prev_name'] = todo.name
        todo.name = request.POST.get('todo_name')
        todo.description = request.POST.get('todo_description')
        todo.save()
        single_todo['id'] = todo.id
        single_todo['name'] = todo.name
        single_todo['description'] = todo.description
        return HttpResponse(json.dumps(single_todo))


@require_POST
def delete(request, todo_id):
    if request.session.get('User') and _is_ajax(request):
        todo = _own_todo(request, todo_id)
        if todo is None:
            return HttpResponseNotFound()
        todo.is_deleted = True
        todo.save()
        single_todo = dict()
        single_todo['id'] = todo.id
        single_todo['name'] = todo.name
        single_todo['description'] = todo.description
        return HttpResponse(json.dumps(single_todo))


@require_POST
def add_todo(request):
    if request.session.get('User') is not None:
        user = User.objects.filter(name=request.session.get('User')).first()
        todo = Todo()
        todo.name = request.POST.get('todo_name')
        todo.description = request.POST.get('todo_description')
        todo.user = user
        todo.save()
        return redirect('todos')
