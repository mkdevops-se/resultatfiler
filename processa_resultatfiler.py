'''
processa_resultatfiler.py
=========================

Ett program för att processera resultatfiler.

'''

import click


def processa_resultatfil(zip_file_path: str, zip_hash: str, zip_url: str, zip_timestamp: str):
    '''Processa en resultat-zipfil.'''

    click.echo(f'Processa fil {zip_file_path} från {zip_url} med hash {zip_hash} ({zip_timestamp})')
