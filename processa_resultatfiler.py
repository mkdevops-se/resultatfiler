#!/usr/bin/env python3
'''
processa_resultatfiler.py
=========================

Ett program för att processera resultatfiler.

'''

import json
import os
import sys
import traceback
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
    if not os.path.exists(zip_file_path):
        raise AssertionError(f'Sökvägen {zip_file_path} existerar inte')

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        if zip_ref.testzip():
            raise AssertionError(f'Korrupt zipfil, "{repr(zip_ref.testzip())}"')
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
@click.argument('log_file_paths', nargs=-1,
                type=click.Path(dir_okay=False, readable=True))
def processa_resultatfiler(log_file_paths: list = None):
    '''Processa en uppsättning zipfiler från nedladdningslogg.'''

    for log_file_path in log_file_paths:
        with open(log_file_path, 'r', encoding='utf-8') as task_log_file:
            log_task_count = 0
            for task_log_entry in task_log_file.readlines():
                log_task_count += 1
                task = json.loads(task_log_entry)
                try:
                    processa_resultatfil(
                        task['zip_file_path'], task['zip_hash'], task['zip_url'], task['zip_ts']
                    )
                except (AssertionError, zipfile.BadZipFile) as err:
                    print(f'Fel vid processering av zipfil {task["zip_file_path"]} från '
                          f'{log_file_path}, rad {log_task_count}:\n'
                          f'{traceback.format_exc()}', file=sys.stderr)

if __name__ == '__main__':
    processa_resultatfiler()
