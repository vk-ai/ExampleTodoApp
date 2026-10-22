"""Widen User.password and hash any existing plain-text passwords in place."""
from django.contrib.auth.hashers import identify_hasher, make_password
from django.db import migrations, models


def hash_plaintext_passwords(apps, schema_editor):
    User = apps.get_model("Todo", "User")
    for user in User.objects.all().iterator():
        try:
            identify_hasher(user.password)
            continue  # already a Django hash
        except ValueError:
            pass
        user.password = make_password(user.password)
        user.save(update_fields=["password"])


class Migration(migrations.Migration):
    dependencies = [("Todo", "0002_todo_is_deleted")]

    operations = [
        migrations.AlterField(model_name="user", name="password",
                              field=models.CharField(max_length=128)),
        # Hashing is one-way, so the reverse is a no-op (hashes stay hashes).
        migrations.RunPython(hash_plaintext_passwords, migrations.RunPython.noop),
    ]
