import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ColorToken",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(db_index=True, default=False)),
                ("name", models.CharField(max_length=100)),
                ("key", models.SlugField(max_length=100)),
                ("mode", models.CharField(
                    choices=[("light", "Light"), ("dark", "Dark")],
                    default="light",
                    max_length=10,
                )),
                ("value", models.CharField(max_length=20)),
                ("group", models.CharField(
                    choices=[
                        ("brand", "Brand"),
                        ("semantic", "Semantic"),
                        ("neutral", "Neutral"),
                        ("custom", "Custom"),
                    ],
                    default="brand",
                    max_length=50,
                )),
                ("description", models.TextField(blank=True, default="")),
                ("order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "appearance_color_tokens",
                "ordering": ["group", "order", "key"],
            },
        ),
        migrations.CreateModel(
            name="MediaAsset",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(db_index=True, default=False)),
                ("name", models.CharField(max_length=100)),
                ("key", models.SlugField(max_length=100, unique=True)),
                ("file", models.ImageField(blank=True, null=True, upload_to="appearance/media/%Y/%m/")),
                ("alt_text", models.CharField(blank=True, default="", max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "appearance_media_assets",
                "ordering": ["key"],
            },
        ),
        migrations.AlterUniqueTogether(
            name="colortoken",
            unique_together={("key", "mode")},
        ),
    ]
