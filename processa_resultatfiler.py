#!/usr/bin/env python3
'''
processa_resultatfiler.py
=========================

Ett program för att processera resultatfiler.

'''

import json
import zipfile

import click
import elasticsearch

es = elasticsearch.Elasticsearch()
health = es.cluster.health()
if __name__ != '__main__':
    click.echo(f'Hälsa för Elasticsearch-kluster "{health["cluster_name"]}", '
               f'status={health["status"]}.')

def _save_datfor(datfor_full: object):
    '''Formattera DATFOR-dokument och spara i Elasticsearch.'''
    pass

def _save_ostfor(ostfor_full: object):
    '''Formattera OSTFOR-dokument och spara i Elasticsearch.'''
    pass

def processa_resultatfil(zip_file_path: str, zip_hash: str, zip_url: str, zip_timestamp: str):
    '''Processa en resultat-zipfil.'''

    click.echo(f'Processa fil {zip_file_path} från {zip_url} med hash {zip_hash} ({zip_timestamp})')

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        if zip_ref.testzip():
            raise Exception(f'Korrupt zipfil, "{repr(zip_ref.testzip())}"')
        for member_name in zip_ref.namelist():
            if not member_name.endswith('.json'):
                continue
            if 'datfor' in member_name:
                with zip_ref.open(member_name) as datfor_json:
                    datfor = json.loads(datfor_json.read())
                    update_ts = datfor['senasteUppdateringstid']
                    updates_count = datfor['antalUppdateringar']
                    click.echo(f'Öppnat och deserialiserat {member_name} med '
                               f'uppdateringstid {update_ts} och {updates_count} uppdateringar')
                    _save_datfor(datfor)
            if 'ostfor' in member_name:
                with zip_ref.open(member_name) as ostfor_json:
                    ostfor = json.loads(ostfor_json.read())
                    update_ts = ostfor['senasteUppdateringstid']
                    updates_count = ostfor['antalUppdateringar']
                    click.echo(f'Öppnat och deserialiserat {member_name} med '
                               f'uppdateringstid {update_ts} och {updates_count} uppdateringar')
                    _save_ostfor(ostfor)


@click.command()
@click.argument('zip_file_paths', nargs=-1,
                type=click.Path(dir_okay=False, resolve_path=True, readable=True))
def processa_resultatfiler(zip_file_paths: list = None):
    '''Processa en uppsättning med zipfiler.'''

    for zip_file_path in zip_file_paths:
        processa_resultatfil(zip_file_path, zip_file_path.split('-')[-1], 'okänd', 'okänd')


if __name__ == '__main__':
    processa_resultatfiler()
