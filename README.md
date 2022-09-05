# resultatfiler

Python-program för att ladda ner resultatfiler (och spara dem i Elasticsearch, snart).

## Getting Started

    # For Elasticsearch on Linux,
    # https://www.elastic.co/guide/en/elasticsearch/reference/5.6/docker.html#_setting_jvm_heap_size
    sysctl -w vm.max_map_count=262144
    docker-compose up -d && docker-compose ps
    python3 -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt
    # Läs in filerna
    ./ladda_resultatfiler.py my.domain.com output_folder
    # Starta worker-processen
    rq worker --with-scheduler

