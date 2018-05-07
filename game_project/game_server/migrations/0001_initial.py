# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-02-05 19:16
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game_List',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_name', models.CharField(max_length=128)),
                ('category', models.CharField(max_length=64)),
                ('description', models.CharField(max_length=512)),
                ('price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('url', models.CharField(max_length=512)),
                ('num_of_purchases', models.PositiveIntegerField(default=0)),
                ('high_score', models.IntegerField(blank=True, default=0, null=True)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Purchased_Games',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('high_score', models.IntegerField(blank=True, default=0)),
                ('game_state', models.TextField(blank=True, default='')),
                ('purchase_time', models.DateTimeField(auto_now_add=True)),
                ('g', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game_server.Game_List')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='User_Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_of_user', models.BooleanField()),
                ('verification_bytes', models.CharField(max_length=64)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]