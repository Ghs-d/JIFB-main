# Generated by Django 5.1.7 on 2025-06-28 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_alter_noticia_corpo'),
    ]

    operations = [
        migrations.AddField(
            model_name='noticia',
            name='tags',
            field=models.CharField(blank=True, help_text='Separe as tags por vírgula', max_length=255),
        ),
    ]
