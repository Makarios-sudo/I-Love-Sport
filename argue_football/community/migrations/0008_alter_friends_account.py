# Generated by Django 4.2.4 on 2023-10-09 09:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
        ("community", "0007_remove_friends_relationship_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="friends",
            name="account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="friends",
                to="users.account",
            ),
        ),
    ]
