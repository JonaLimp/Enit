# Generated by Django 5.1.3 on 2024-11-29 17:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Region",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("code", models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Sector",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Substance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="RealtimeEnvironmentalRecord",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", models.FloatField()),
                ("timestamp", models.DateTimeField()),
                (
                    "region",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="environmental_data.region",
                    ),
                ),
                (
                    "sector",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="environmental_data.sector",
                    ),
                ),
                (
                    "substance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="environmental_data.substance",
                    ),
                ),
            ],
            options={
                "ordering": ["-timestamp"],
                "abstract": False,
                "unique_together": {("region", "substance", "timestamp")},
            },
        ),
        migrations.CreateModel(
            name="HistoricalEnvironmentalRecord",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", models.FloatField()),
                ("timestamp", models.DateTimeField()),
                (
                    "region",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="environmental_data.region",
                    ),
                ),
                (
                    "sector",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="environmental_data.sector",
                    ),
                ),
                (
                    "substance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="environmental_data.substance",
                    ),
                ),
            ],
            options={
                "ordering": ["-timestamp"],
                "abstract": False,
                "unique_together": {("region", "substance", "timestamp")},
            },
        ),
    ]
