'''
processa_resultatfiler.py
=========================

Ett program för att processera resultatfiler.

'''

import click
import elasticsearch

es = elasticsearch.Elasticsearch()
health = es.cluster.health()
click.echo(f'Hälsa för Elasticsearch-kluster "{health["cluster_name"]}", '
           f'status={health["status"]}.')

def processa_resultatfil(zip_file_path: str, zip_hash: str, zip_url: str, zip_timestamp: str):
    '''Processa en resultat-zipfil.'''

    click.echo(f'Processa fil {zip_file_path} från {zip_url} med hash {zip_hash} ({zip_timestamp})')
