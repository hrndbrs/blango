# Generated by Django 3.2.24 on 2024-02-20 00:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20240206_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='published_at',
            field=models.DateTimeField(auto_now=True, db_index=True, null=True),
        ),
    ]
