# Migração segura: converte FK ghs → ManyToMany classificacoes_ghs preservando vínculos existentes.

from django.db import migrations, models


def migrar_ghs_para_m2m(apps, schema_editor):
    """Copia a classificação GHS única (FK) para o novo relacionamento N:N."""
    Reagente = apps.get_model('estoque', 'Reagente')

    for reagente in Reagente.objects.exclude(ghs_id=None):
        reagente.classificacoes_ghs.add(reagente.ghs_id)


def reverter_m2m_para_ghs(apps, schema_editor):
    """Reversão: restaura a FK com a primeira classificação GHS do reagente."""
    Reagente = apps.get_model('estoque', 'Reagente')

    for reagente in Reagente.objects.all():
        primeira_ghs = reagente.classificacoes_ghs.order_by('id').first()
        if primeira_ghs is not None:
            reagente.ghs_id = primeira_ghs.id
            reagente.save(update_fields=['ghs_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0003_populate_ghs'),
    ]

    operations = [
        # 1. Cria o novo campo N:N sem remover a FK antiga.
        migrations.AddField(
            model_name='reagente',
            name='classificacoes_ghs',
            field=models.ManyToManyField(
                blank=True,
                help_text='Pictogramas GHS aplicáveis ao reagente (pode haver mais de um).',
                related_name='reagentes',
                to='estoque.ghs',
                verbose_name='Classificações GHS',
            ),
        ),
        # 2. Transfere os dados da FK para o M2M antes de apagar a coluna antiga.
        migrations.RunPython(migrar_ghs_para_m2m, reverter_m2m_para_ghs),
        # 3. Remove a FK legada somente após a cópia dos dados.
        migrations.RemoveField(
            model_name='reagente',
            name='ghs',
        ),
    ]
