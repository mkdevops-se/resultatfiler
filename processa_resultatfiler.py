#!/usr/bin/env python3
'''
processa_resultatfiler.py
=========================

Ett program för att processera resultatfiler.

'''

import json
import zipfile

import click
#import elasticsearch

#es = elasticsearch.Elasticsearch()
#health = es.cluster.health()
#if __name__ != '__main__':
#    click.echo(f'Hälsa för Elasticsearch-kluster "{health["cluster_name"]}", '
#               f'status={health["status"]}.')

def _save_prel_mandatfordelning(mandatfordelning_full: object):
    '''Formattera prel. mandatfördelning-dokument och spara i t.ex. Elasticsearch.'''
    pass
    # TODO: Logic for document handling.

def _save_prel_rostfordelning(rostfordelning_full: object):
    '''Formattera prel. rostfördelning-dokument och spara i t.ex. Elasticsearch.'''
    pass
    # TODO: Logic for document handling.

def _save_slutl_mandatfordelning(mandatfordelning_full: object):
    '''Formattera slutlig mandatfördelning-dokument och spara i t.ex. Elasticsearch.'''
    pass
    # TODO: Logic for document handling.

def _save_slutl_rostfordelning(rostfordelning_full: object):
    '''Formattera slutlig rostfördelning-dokument och spara i t.ex. Elasticsearch.'''
    pass
    # TODO: Logic for document handling.

def processa_resultatfil(zip_file_path: str, zip_hash: str, zip_url: str, zip_timestamp: str):
    '''Processa en resultat-zipfil.'''

    click.echo(f'Processa fil {zip_file_path} från {zip_url} med hash {zip_hash} ({zip_timestamp})')

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        if zip_ref.testzip():
            raise Exception(f'Korrupt zipfil, "{repr(zip_ref.testzip())}"')
        for member_name in zip_ref.namelist():
            if not member_name.endswith('.json'):
                continue
            if 'mandatfordelning' in member_name:
                with zip_ref.open(member_name) as mandatfordelning_json:
                    mandatfordelning = json.loads(mandatfordelning_json.read())
                    update_ts = mandatfordelning['senasteUppdateringstid']
                    updates_count = mandatfordelning['antalUppdateringar']
                    click.echo(f'Öppnat och deserialiserat {member_name} med '
                               f'uppdateringstid {update_ts} och {updates_count} uppdateringar')
                    if 'preliminar' in member_name:
                        _save_prel_mandatfordelning(mandatfordelning)
                    elif 'slutlig' in member_name:
                        _save_slutl_mandatfordelning(mandatfordelning)
                    else:
                        raise AssertionError(f'Felaktigt filnamn {member_name}')
            if 'rostfordelning' in member_name:
                with zip_ref.open(member_name) as rostfordelning_json:
                    rostfordelning = json.loads(rostfordelning_json.read())
                    update_ts = rostfordelning['senasteUppdateringstid']
                    updates_count = rostfordelning['antalUppdateringar']
                    click.echo(f'Öppnat och deserialiserat {member_name} med '
                               f'uppdateringstid {update_ts} och {updates_count} uppdateringar')
                    if 'preliminar' in member_name:
                        _save_prel_rostfordelning(rostfordelning)
                    elif 'slutlig' in member_name:
                        _save_slutl_rostfordelning(rostfordelning)
                    else:
                        raise AssertionError(f'Felaktigt filnamn {member_name}')


@click.command()
@click.argument('zip_file_paths', nargs=-1,
                type=click.Path(dir_okay=False, resolve_path=True, readable=True))
def processa_resultatfiler(zip_file_paths: list = None):
    '''Processa en uppsättning med zipfiler.'''

    for zip_file_path in zip_file_paths:
        processa_resultatfil(zip_file_path, zip_file_path.split('-')[-1], 'okänd', 'okänd')


if __name__ == '__main__':
    processa_resultatfiler()
