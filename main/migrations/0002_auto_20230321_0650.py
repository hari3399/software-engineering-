# Generated by Django 2.2.28 on 2023-03-21 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='packagesubscription',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]