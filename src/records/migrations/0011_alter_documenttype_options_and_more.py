# Generated by Django 5.2 on 2025-04-04 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0010_alter_notification_options_notification_created_at_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='documenttype',
            options={'verbose_name': 'Тип документа', 'verbose_name_plural': 'Типы документов'},
        ),
        migrations.AlterField(
            model_name='documenttype',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='documenttype',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Название'),
        ),
    ]
