# Generated by Django 5.2.1 on 2025-05-21 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_alter_noticia_corpo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noticia',
            name='capa_noticia',
            field=models.ImageField(upload_to='uploads/noticias/CAPAS/%Y/%m/%d'),
        ),
        migrations.AlterField(
            model_name='noticia',
            name='corpo',
            field=models.FileField(upload_to='uploads/noticias/noticias/%Y/%m/%d'),
        ),
    ]
