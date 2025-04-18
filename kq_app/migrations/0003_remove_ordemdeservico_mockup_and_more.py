# Generated by Django 4.1.5 on 2024-12-11 13:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kq_app", "0002_cliente_endereco_completo_ordemdeservico_arte_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="ordemdeservico",
            name="mockup",
        ),
        migrations.RemoveField(
            model_name="ordemdeservico",
            name="personalizacao",
        ),
        migrations.AlterField(
            model_name="produto",
            name="material",
            field=models.CharField(
                choices=[
                    ("malhaalgodao", "Malha Algodão"),
                    ("cottonelastano", "Cotton Elastano"),
                    ("moletomstrong", "Moletom Strong"),
                    ("moletombasic", "Moletom Basic"),
                    ("dryfit", "Dry Fit"),
                    ("poliamida", "Poliamida"),
                    ("malhacanelada", "Malha Canelada"),
                    ("piquet", "Piquet"),
                ],
                default="malhaalgodao",
                max_length=15,
            ),
        ),
    ]
