#!/usr/bin/env python3
'''
ladda_resultatfiler.py
======================

Ett program för att ladda ner resultatfiler.

'''

import os
import datetime
import json
import time

import shutil
import requests
import click
import rq
import redis

from processa_resultatfiler import processa_resultatfil

queue = rq.Queue(connection=redis.Redis())

REQ_COUNTER = 0
REQ_SLEEP = 0.10

def _get_default_headers(bust_rate_limiter=False):
    # pylint: disable=C0103
    global REQ_COUNTER
    REQ_COUNTER += 1
    user_agent = 'Din van i noden, Python Requests och RQ'
    if bust_rate_limiter:
        user_agent = f'Req {REQ_COUNTER}: {user_agent}'
    return {
        'User-Agent': user_agent,
        'X-Username': 'mblomdahl'
    }

def _hamta_indexfil(indexurl: str):
    index_ts = datetime.datetime.utcnow()
    indexfil = requests.get(indexurl, headers=_get_default_headers(), timeout=(3, 7))
    click.echo(f'Indexfil inläst med status {indexfil.status_code}, '
               f'bytes: {len(indexfil.content)} ({index_ts.isoformat()}).')
    if indexfil.status_code != 200:
        raise Exception(f'Ej 200 OK från index-URL {indexurl}: {indexfil.content}')
    if len(indexfil.content) < 24:
        raise Exception(f'Corrupt index-innehåll, "{indexfil.content}"')
    time.sleep(REQ_SLEEP)
    return indexfil

def _skapa_download_tasks(indexfil_domain, output_dir, index_url):
    index_file = _hamta_indexfil(index_url)
    download_tasks = []
    for line in index_file.iter_lines():
        zip_hash, zip_path = line.split()
        if not zip_path or len(zip_path) < 8:
            click.echo(f'Tom filsökväg för hash {zip_hash}, ignorerar.')
            continue
        zip_path_no_dotslash = zip_path.decode('utf-8').replace("./", "")
        download_tasks.append({
            'zip_hash': zip_hash.decode("utf-8"),
            'zip_file_path': f'{output_dir}/{zip_path_no_dotslash}-{zip_hash.decode("utf-8")}',
            'zip_url': f'https://{indexfil_domain}/resultatfiler/{zip_path_no_dotslash}',
            'zip_ts': datetime.datetime.utcnow().isoformat().split('.')[0] + 'Z'
        })
    return download_tasks

def _download_and_enqueue(task):
    time.sleep(REQ_SLEEP)
    download_ts = datetime.datetime.utcnow()
    click.echo(f'Ladda ner {task["zip_url"]} till {task["zip_file_path"]} '
               f'({download_ts.isoformat()}) ...')
    zipfil = requests.get(task['zip_url'], headers=_get_default_headers(), timeout=(3, 7),
                          stream=True)
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

@click.command()
@click.argument('indexfil_domain', type=click.STRING)
@click.argument('output_dir', type=click.Path(file_okay=False, resolve_path=True, writable=True))
@click.option('-p', '--poll_interval', default=30, type=click.IntRange(0, 3600),
              help='Polla med intervall av N sekunder, inaktivera med 0')
def ladda_ner_resultatfiler(indexfil_domain: str = None, output_dir: str = None,
                            poll_interval: int = None):
    """Ladda ner index-fil med resultatfiler och deras hashar."""

    invocation_ts = datetime.datetime.utcnow()
    logfile = f'{output_dir}/tasks-{invocation_ts.strftime("%y%m%dT%H%M%S")}.log'

    index_url = f'https://{indexfil_domain}/resultatfiler/index.md5'

    while True:
        loop_t0 = datetime.datetime.utcnow()
        download_tasks = _skapa_download_tasks(indexfil_domain, output_dir, index_url)
        for task in download_tasks:
            if os.path.exists(task['zip_file_path']):
                continue
            _download_and_enqueue(task)
            with open(logfile, 'a', encoding='utf-8') as task_log_file:
                task_log_file.write(json.dumps(task) + '\n')
        loop_t1 = datetime.datetime.utcnow()

        runtime_sec = int((loop_t1 - invocation_ts).total_seconds())
        if not poll_interval:
            click.echo(f'Polling deaktiverad, avbryter efter {runtime_sec:d} sek körtid.')
            break

        next_poll_delay_sec = poll_interval - (loop_t1 - loop_t0).total_seconds()
        if next_poll_delay_sec > 0:
            click.echo(f'Nästa pollning om {next_poll_delay_sec:.1f} sek '
                       f'(total körtid {runtime_sec:d} sek, ctrl+c för att avbryta) ...')
            time.sleep(next_poll_delay_sec)

if __name__ == '__main__':
    ladda_ner_resultatfiler()
