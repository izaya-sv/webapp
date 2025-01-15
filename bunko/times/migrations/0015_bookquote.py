# Generated by Django 4.2.14 on 2025-01-03 18:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('times', '0014_timesmedia_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookQuote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quote', models.TextField()),
                ('libro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='times.book')),
            ],
        ),
    ]