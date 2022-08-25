#!/usr/bin/env python3
'''
ladda_resultatfiler.py
======================

Ett program för att ladda ner resultatfiler.

'''

import os
import datetime

import shutil
import requests
import click
import rq
import redis

from processa_resultatfiler import processa_resultatfil

queue = rq.Queue(connection=redis.Redis())

@click.command()
@click.argument('indexfil_domain', type=click.STRING)
@click.argument('output_dir', type=click.Path(file_okay=False, resolve_path=True, writable=True))
def ladda_ner_resultatfiler(indexfil_domain: str = None, output_dir: str = None):
    """Ladda ner index-fil med resultatfiler och deras hashar."""

    indexurl = f'https://{indexfil_domain}/resultatfiler/index.md5'
    indexfil = requests.get(indexurl)
    click.echo(f'Indexfil inläst med status {indexfil.status_code}, bytes: {len(indexfil.content)}')
    if indexfil.status_code != 200:
        raise Exception(f'Ej 200 OK från index-URL {indexurl}: {indexfil.content}')
    if len(indexfil.content) < 48:
        raise Exception(f'Corrupt index-innehåll, "{indexfil.content}"')

    download_tasks = []
    for line in indexfil.iter_lines():
        zip_hash, zip_path = line.split()
        zip_path_no_dotslash = zip_path.decode('utf-8').replace("./", "")
        download_tasks.append({
            'zip_hash': zip_hash.decode("utf-8"),
            'zip_file_path': f'{output_dir}/{zip_path_no_dotslash}-{zip_hash.decode("utf-8")}',
            'zip_url': f'https://{indexfil_domain}/resultatfiler/{zip_path_no_dotslash}'
        })

    for task in download_tasks:
        if os.path.exists(task['zip_file_path']):
            continue
        download_ts = datetime.datetime.utcnow()
        click.echo(f'Ladda ner {task["zip_url"]} till {task["zip_file_path"]} '
                   f'({download_ts.isoformat()})...')
        zipfil = requests.get(task['zip_url'], stream=True)
        os.makedirs(os.path.dirname(task['zip_file_path']), exist_ok=True)
        with open(task['zip_file_path'], 'wb') as local_file:
            shutil.copyfileobj(zipfil.raw, local_file)
        process_ts = datetime.datetime.utcnow()
        job = queue.enqueue(
            processa_resultatfil,
            task['zip_file_path'],
            task['zip_hash'],
            task['zip_url'],
            process_ts.isoformat()
        )

        click.echo(f'Processeringsjobb {job.id} köat för {task["zip_file_path"]} '
                   f'({process_ts.isoformat()}).')

if __name__ == '__main__':
    ladda_ner_resultatfiler()
