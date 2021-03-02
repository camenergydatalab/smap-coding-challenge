# Generated by Django 2.2.15 on 2021-03-02 06:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.IntegerField(editable=False, primary_key=True, serialize=False)),
                ('area', models.CharField(max_length=2, verbose_name='area')),
                ('tariff', models.CharField(max_length=2, verbose_name='tariff')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
        ),
        migrations.CreateModel(
            name='Consumption',
            fields=[
                ('id', models.IntegerField(editable=False, primary_key=True, serialize=False)),
                ('datetime', models.DateTimeField(unique_for_date=True, verbose_name='datetime')),
                ('consumption', models.DecimalField(decimal_places=1, max_digits=10, verbose_name='consumption')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='consumption.User')),
            ],
            options={
                'verbose_name': 'Consumption',
                'verbose_name_plural': 'Consumption',
            },
        ),
    ]
