# Generated by Django 5.0.2 on 2024-02-12 12:53

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DocumentTemplate",
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
                ("name", models.CharField(max_length=100)),
                ("template_file", models.FileField(upload_to="agreements_templates/")),
            ],
            options={
                "verbose_name": "Шаблон договора",
                "verbose_name_plural": "Шаблоны договоров",
            },
        ),
    ]
