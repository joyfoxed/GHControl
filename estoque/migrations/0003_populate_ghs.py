# Data migration: carga inicial dos 9 pictogramas GHS padrão (Sistema Globalmente Harmonizado).

from django.db import migrations

# Nomes oficiais e caminhos relativos dos pictogramas GHS (GHS01 a GHS09).
PICTOGRAMAS_GHS = [
    ('Explosivo', 'pictogramas/ghs01_explosivo.png'),
    ('Inflamável', 'pictogramas/ghs02_inflamavel.png'),
    ('Comburente', 'pictogramas/ghs03_comburente.png'),
    ('Gás sob pressão', 'pictogramas/ghs04_gas_sob_pressao.png'),
    ('Corrosivo', 'pictogramas/ghs05_corrosivo.png'),
    ('Toxicidade aguda (Caveira)', 'pictogramas/ghs06_toxicidade_aguda.png'),
    (
        'Irritante/Perigoso à camada de ozônio (Exclamação)',
        'pictogramas/ghs07_irritante.png',
    ),
    (
        'Mutagênico/Carcinogênico (Perigo à saúde)',
        'pictogramas/ghs08_perigo_a_saude.png',
    ),
    (
        'Perigoso ao meio ambiente (Aquático)',
        'pictogramas/ghs09_perigoso_ao_meio_ambiente.png',
    ),
]


def popular_pictogramas_ghs(apps, schema_editor):
    """Insere os 9 pictogramas GHS padrão, apenas se ainda não existirem."""
    GHS = apps.get_model('estoque', 'GHS')

    for nome, picto in PICTOGRAMAS_GHS:
        GHS.objects.get_or_create(nome=nome, defaults={'picto': picto})


def remover_pictogramas_ghs(apps, schema_editor):
    """Reverte a carga inicial removendo apenas os registros criados por esta migração."""
    GHS = apps.get_model('estoque', 'GHS')
    nomes = [nome for nome, _ in PICTOGRAMAS_GHS]
    GHS.objects.filter(nome__in=nomes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0002_historico_movimentacao'),
    ]

    operations = [
        migrations.RunPython(popular_pictogramas_ghs, remover_pictogramas_ghs),
    ]
