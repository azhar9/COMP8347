# Generated by Django 4.2.2 on 2023-07-03 15:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('onlinelearningapp', '0002_alter_coursecontent_options_alter_section_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enrollment',
            name='enrolled',
        ),
    ]
