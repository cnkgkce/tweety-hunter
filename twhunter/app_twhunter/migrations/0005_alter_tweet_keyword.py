# Generated by Django 4.1 on 2022-08-15 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_twhunter", "0004_alter_tweet_keyword"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tweet",
            name="keyword",
            field=models.ManyToManyField(
                blank=True, null=True, related_name="tweets", to="app_twhunter.keyword"
            ),
        ),
    ]
