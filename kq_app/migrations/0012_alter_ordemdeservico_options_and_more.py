# Generated by Django 4.1.5 on 2025-03-02 23:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("kq_app", "0011_remove_produto_codigo_barras_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="ordemdeservico",
            options={
                "ordering": ["numero_os"],
                "verbose_name": "Ordem de Serviço",
                "verbose_name_plural": "Ordens de Serviço",
            },
        ),
        migrations.AddField(
            model_name="ordemdeservico",
            name="numero_os",
            field=models.IntegerField(
                blank=True, null=True, verbose_name="Número da OS"
            ),
        ),
        migrations.AlterField(
            model_name="ordemdeservico",
            name="pedido",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ordens_de_servico",
                to="kq_app.pedido",
                verbose_name="Pedido",
            ),
        ),
    ]
