# Generated by Django 3.2.16 on 2024-07-01 09:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_alter_comment_post_object'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='post_object',
            new_name='post',
        ),
    ]
