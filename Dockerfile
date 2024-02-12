FROM docker.elastic.co/elasticsearch/elasticsearch:8.12.1
RUN elasticsearch-plugin install --batch https://github.com/alexklibisz/elastiknn/releases/download/8.12.1.0/elastiknn-8.12.1.0.zip