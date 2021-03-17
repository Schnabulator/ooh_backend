# Generated by Django 3.1.7 on 2021-03-09 14:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ooh', '0010_auto_20210309_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oohuser',
            name='defaultEventLocation',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ooh.eventlocation'),
        ),
        migrations.AlterField(
            model_name='oohuser',
            name='housenumber',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='oohuser',
            name='locationID',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='ooh.location'),
        ),
        migrations.AlterField(
            model_name='oohuser',
            name='street',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
