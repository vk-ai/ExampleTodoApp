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

        r = self.client.post(f"/delete/{todo.id}/", **AJAX)
        self.assertEqual(r.status_code, 200)
        todo.refresh_from_db()
        self.assertTrue(todo.is_deleted)

    def test_todos_requires_login(self):
        self.assertRedirects(self.client.get("/todos"), "/", fetch_redirect_response=False)

    def test_admin_login_page(self):
        self.assertEqual(self.client.get("/admin/login/").status_code, 200)


from django.contrib.auth.hashers import check_password, identify_hasher
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import Client, TransactionTestCase


class PasswordHashingTests(TestCase):
    def test_signup_stores_hash_not_plaintext(self):
        self.client.post("/signin", {"name": "alice", "password": "s3cret-pw"})
        stored = User.objects.get(name="alice").password
        self.assertNotEqual(stored, "s3cret-pw")
        identify_hasher(stored)  # raises if not a Django hash
        self.assertTrue(check_password("s3cret-pw", stored))

    def test_duplicate_name_signup_rejected(self):
        self.client.post("/signin", {"name": "alice", "password": "one"})
        c = Client()
        r = c.post("/signin", {"name": "alice", "password": "two"})
        self.assertRedirects(r, "/", fetch_redirect_response=False)
        self.assertEqual(User.objects.filter(name="alice").count(), 1)


class HashMigrationTests(TransactionTestCase):
    def test_migration_hashes_existing_plaintext_rows(self):
        ex = MigrationExecutor(connection)
        ex.migrate([("Todo", "0002_todo_is_deleted")])
        OldUser = ex.loader.project_state([("Todo", "0002_todo_is_deleted")]).apps.get_model("Todo", "User")
        OldUser.objects.create(name="legacy", password="plain-pw")
        ex = MigrationExecutor(connection)
        ex.loader.build_graph()
        ex.migrate([("Todo", "0003_hash_user_passwords")])
        u = User.objects.get(name="legacy")
        identify_hasher(u.password)
        self.assertTrue(u.check_password("plain-pw"))
        self.assertEqual(Client().post("/login", {"name": "legacy", "password": "plain-pw"}).url, "/todos")


class CsrfAndOwnershipTests(TestCase):
    def setUp(self):
        self.c = Client(enforce_csrf_checks=True)
        for name in ("owner", "intruder"):
            u = User(name=name); u.set_password("pw"); u.save()
        self.todo = Todo.objects.create(name="mine", description="d",
                                        user=User.objects.get(name="owner"))

    def _login(self, client, name):
        r = client.get("/")
        token = r.cookies["csrftoken"].value
        client.post("/login", {"name": name, "password": "pw", "csrfmiddlewaretoken": token})
        return token

    def test_add_and_edit_reject_missing_csrf(self):
        self._login(self.c, "owner")
        self.assertEqual(self.c.post("/add_todo", {"todo_name": "x", "todo_description": "y"}).status_code, 403)
        self.assertEqual(self.c.post(f"/edit/{self.todo.id}", {"todo_name": "x"}, **AJAX).status_code, 403)
        self.assertEqual(self.c.post(f"/delete/{self.todo.id}/", **AJAX).status_code, 403)

    def test_add_and_edit_accept_valid_csrf(self):
        token = self._login(self.c, "owner")
        r = self.c.post("/add_todo", {"todo_name": "x", "todo_description": "y"}, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(r.status_code, 302)
        r = self.c.post(f"/edit/{self.todo.id}", {"todo_name": "n2", "todo_description": "d2"},
                        HTTP_X_CSRFTOKEN=token, **AJAX)
        self.assertEqual(r.status_code, 200)

    def test_delete_via_get_not_allowed(self):
        self._login(self.c, "owner")
        self.assertEqual(self.c.get(f"/delete/{self.todo.id}/", **AJAX).status_code, 405)

    def test_cannot_touch_other_users_todo(self):
        token = self._login(self.c, "intruder")
        self.assertEqual(self.c.get(f"/todo/{self.todo.id}/").status_code, 404)
        r = self.c.post(f"/edit/{self.todo.id}", {"todo_name": "pwned", "todo_description": "x"},
                        HTTP_X_CSRFTOKEN=token, **AJAX)
        self.assertEqual(r.status_code, 404)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.name, "mine")
