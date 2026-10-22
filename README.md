# README #

This README would normally document whatever steps are necessary to get your application up and running.

### How do I set up? ###

* Install all Requirements using requirements.txt
* Create a Database in MYSQL with name UserTodo
* For MySQL, set TODO_DB_* environment variables (see .env.example); never put passwords in settings.py
* python manage.py migrate
* python manage.py createsuperuser

Left Work is Adding Comments 

If You Can Do ,do it and Inform Me before Tommorow Morning

## Configuration and security

Set `DJANGO_SECRET_KEY` (required unless `DJANGO_DEBUG=true`), `DJANGO_DEBUG` (default false) and
`DJANGO_ALLOWED_HOSTS`; see `.env.example`. Passwords are stored as Django password hashes
(migration `0003` hashes any existing plain-text rows). The add/edit/delete views are
CSRF-protected and only act on the logged-in user's own todos.
