# Generated by Django 4.1 on 2022-08-23 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_twhunter", "0014_remove_keyword_counter"),
    ]

    operations = [
        migrations.AddField(
            model_name="keyword",
            name="counter",
            field=models.IntegerField(default=0),
        ),
    ]