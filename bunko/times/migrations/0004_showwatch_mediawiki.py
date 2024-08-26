# Generated by Django 4.2.14 on 2024-07-17 14:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('times', '0003_moviewatch'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShowWatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_d', models.DateField()),
                ('finish_d', models.DateField()),
                ('sseason', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='times.season')),
            ],
        ),
        migrations.CreateModel(
            name='MediaWiki',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_type', models.IntegerField()),
                ('media_id', models.IntegerField()),
                ('mwiki', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='times.wiki')),
            ],
        ),
    ]
