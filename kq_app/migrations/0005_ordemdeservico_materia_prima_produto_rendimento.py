# Generated by Django 4.1.5 on 2024-12-19 01:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kq_app", "0004_material_tipoproduto_remove_produto_nome_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="ordemdeservico",
            name="materia_prima",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AddField(
            model_name="produto",
            name="rendimento",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
