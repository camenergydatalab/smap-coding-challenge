# Generated by Django 2.2.15 on 2024-02-05 02:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Consumer',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('area', models.CharField(max_length=255)),
                ('tariff', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Consumption',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('datetime', models.DateTimeField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('consumer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='consumption.Consumer')),
            ],
            options={
                'unique_together': {('consumer', 'datetime')},
            },
        ),
    ]