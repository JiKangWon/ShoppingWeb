# Generated by Django 5.1.1 on 2025-04-07 15:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('price', models.IntegerField(default=1)),
                ('category', models.CharField(default='Other', max_length=100)),
                ('quantity', models.IntegerField(default=0)),
                ('img_url', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('available', 'Available'), ('sold', 'Sold'), ('hide', 'Hide')], default='Sold', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('preparing', 'Preparing'), ('pending', 'Pending'), ('completed', 'Completed')], default='Preparing', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=30)),
                ('balance', models.IntegerField(default=0)),
                ('role', models.CharField(choices=[('user', 'user'), ('seller', 'seller')], default='user', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product_Quantity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_site.product')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_site.transaction')),
            ],
        ),
        migrations.AddField(
            model_name='transaction',
            name='buyer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='main_site.user'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='main_site.user'),
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_site.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_site.user')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_site.user'),
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_site.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_site.user')),
            ],
        ),
    ]
