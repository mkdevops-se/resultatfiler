# resultatfiler

Python-program för att ladda ner resultatfiler (och spara dem i Elasticsearch, snart).

## Getting Started

Förutsättningar: Mac eller Linux med Git LFS, Docker Compose och Python 3.8+, därefter...

    git clone git@github.com:mkdevops-se/resultatfiler.git
    cd resultatfiler/
    docker-compose up -d && docker-compose ps
    python3 -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt
    # Läs in filerna
    ./ladda_resultatfiler.py resultat.val.se 20220911
    # Starta worker-processen
    rq worker --with-scheduler

Eller, för att processera igenom arkiverade resultatfiler baserat på nedladdningsloggarna:

    tar -x --directory=./20220911 -f 20220911/220915_prel_resultatfiler.tgz
    ./processa_resultatfiler.py 20220911/tasks-220911T*.log > process.log 2> error.log

(Körtid cirka 5 minuter.)
