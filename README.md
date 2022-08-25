# resultatfiler

Python-program för att ladda ner resultatfiler.

## Getting Started

    docker-compose up -d && docker-compose ps
    python3 -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt
    # Läs in filerna
    ./ladda_resultatfiler.py my.domain.com output_folder
    # Starta worker-processen
    rq worker --with-scheduler

