# Generated by Django 1.10.7 on 2017-08-08 16:21


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0013_auto_20170807_1930'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='use_old_smileys',
            field=models.BooleanField(default=False, verbose_name='Utilise les anciens smileys ?'),
        ),
    ]
