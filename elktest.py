#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import logging
from elasticsearch import Elasticsearch

INDEX_NAME = 'gpon1'


def create_index(es_object, index_name=INDEX_NAME):
    created = False
    # index settings
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "ont": {
                "properties": {
                    "id": {
                        "type": "integer"
                    },
                    "port": {
                        "type": "text"
                    },
                    "sn": {
                        "type": "text"
                    },
                    "distance": {
                        "type": "float"
                    },
                    "tx": {
                        "type": "float"
                    },
                    "rx": {
                        "type": "float"
                    },
                    "description": {
                        "type": "text"
                    },
                    "lastuptime": {
                        "type": "date"
                    },
                    "lastdowntime": {
                        "type": "date"
                    },
                    "lastdowncause": {
                        "type": "text"
                    },
                    "datetime": {
                        "type": "date"
                    },
                    "type": {
                        "type": "text"
                    },
                }
            }
        }
    }
    try:
        if not es_object.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist error"
            es_object.indices.create(index=index_name, ignore=400, body=settings)
            print('Created Index')
            created = True
        else:
            print('indice exists')
    except Exception as ex:
        print(str(ex))
    finally:
        return created


def search(es_object, index_name, search):
    res = es_object.search(index=index_name, body=search)
    return res


def store_record(elastic_object, index_name, record):
    try:
        outcome = elastic_object.index(index=index_name, doc_type='ont', body=record)
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))


def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if _es.ping():
        print('Yay Connect')
    else:
        print('Awww it could not connect!')
    return _es


if __name__ == '__main__':
    e = connect_elasticsearch()
    create_index(e)
    if e is not None:
        # test insert a record
        record = {
            "status": "online",
            "distance": "97",
            "description": "LG-MB1-ENG-ONT02",
            "tx": "2.08",
            "rx": "-14.11",
            "lastuptime": "2019-07-17",
            "id": "2",
            "lastdowntime": "2019-07-17",
            "sn": "485754432EC65E9C",
            "lastdowncause": "dying-gasp",
            "datetime": "2019-11-20",
            "type": "EG8080P",
            "port": "0/0/0"
        }
    store_record(e, INDEX_NAME, record)
    # test search
    res = search_object = {'query': {'match': {'id': '1'}}}
    print (res)
    res = search(e, INDEX_NAME, json.dumps(search_object))
    print (res)

logging.basicConfig(level=logging.ERROR)
