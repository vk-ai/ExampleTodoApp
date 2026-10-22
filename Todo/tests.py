"""Offline smoke tests (SQLite): python manage.py test"""
import json

from django.test import TestCase

from Todo.models import Todo, User

AJAX = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}


class SmokeTests(TestCase):
    def test_home_renders(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "csrfmiddlewaretoken")

    def test_signup_login_todo_flow(self):
        r = self.client.post("/signin", {"name": "vk", "password": "pw"})
        self.assertRedirects(r, "/todos", fetch_redirect_response=False)
        self.assertTrue(User.objects.filter(name="vk").exists())

        r = self.client.post("/login", {"name": "vk", "password": "pw"})
        self.assertRedirects(r, "/todos", fetch_redirect_response=False)
        r = self.client.post("/login", {"name": "vk", "password": "bad"})
        self.assertRedirects(r, "/", fetch_redirect_response=False)
        self.client.post("/login", {"name": "vk", "password": "pw"})

        self.client.post("/add_todo", {"todo_name": "t1", "todo_description": "d1"})
        todo = Todo.objects.get(name="t1")
        self.assertContains(self.client.get("/todos"), "t1")

        r = self.client.get(f"/todo/{todo.id}/")
        self.assertEqual(json.loads(r.content)["name"], "t1")

        r = self.client.post(f"/edit/{todo.id}", {"todo_name": "t2", "todo_description": "d2"}, **AJAX)
        self.assertEqual(json.loads(r.content)["prev_name"], "t1")

        r = self.client.get(f"/delete/{todo.id}/", **AJAX)
        self.assertEqual(r.status_code, 200)
        todo.refresh_from_db()
        self.assertTrue(todo.is_deleted)

    def test_todos_requires_login(self):
        self.assertRedirects(self.client.get("/todos"), "/", fetch_redirect_response=False)

    def test_admin_login_page(self):
        self.assertEqual(self.client.get("/admin/login/").status_code, 200)
