#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
TODO for this version: 
1, print the file name to be processed for troubleshooting
2, move the prossed file into the output folder
3, Seems it takes too long to process 
'''
import time
import os
import shutil
import json
from glob import iglob
from pprint import pprint
from time import sleep
from elasticsearch import Elasticsearch

stripTime = True
isTestES = False
isTest = True
DATETIME = 0
SHIFT = 5  # may vary?
INDEX_NAME = 'gpon3'
TIMESTAMP = 0

#
# updated 20191129:
# 1, field 'datetime' cannot has space
# 2, all datetime field, with time error. remove the time temporary
# 3, direct send to the elk after get the ont
# TODO: will add time in the datetime fields


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


def send2elk(ont_list):
    e = connect_elasticsearch()
    create_index(e)
    if e is not None:
        for o in ont_list['ont']:
            try:
                record = {
                    "datetime": o["datetime"],
                    "id": o["id"],
                    "port": o["port"],
                    "status": o["status"],
                    "distance": o["distance"],
                    "description": o["description"],
                    "tx": o["tx"] if o["status"] == "online" else -1000,
                    "rx": o["rx"] if o["status"] == "online" else -1000,
                    "lastuptime": o["lastuptime"],
                    "lastdowntime": o["lastdowntime"],
                    "sn": o["sn"],
                    "lastdowncause": o["lastdowncause"],
                    "type": o["type"],
                }
            except Exception as ex:
                print('Error in send2elk')
                print(str(ex))
                print(o)
            
            store_record(e, index_name=INDEX_NAME, record=record)
            sleep(2)


def store_record(elastic_object, index_name, record):
    outcome = ""
    try:
        outcome = elastic_object.index(index=index_name, doc_type='ont', body=record)
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))
    finally:
        print("recorded:")
        print(record) if isTest else None

def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if _es.ping():
        print('Yay Connect')
    else:
        print('Awww it could not connect!')
    return _es


def search(es_object, index_name, search):
    res = es_object.search(index=index_name, body=search)
    pprint(res)


def formalize(array):
    newlist = []
    for item in array:
        if item and item != '\n':
            newlist.append(str(item))
    return newlist


def jsonConcat(ontdata, ontdata_1):
    for _ont in ontdata_1["ont"]:
        ontdata["ont"].append(_ont)
    return ontdata


def set_olt_data(_lines):
    ont_data = {}
    ont_data['ont'] = []
    i = 0
    while i < len(_lines):
        line = _lines[i]
        _port = get_port_number(line)
        try:
            port = get_port_number(line)
            if not port:
                i = i + 1
                continue
            _ont_count = get_ont_count(line)  # ont count differs with port
            if _ont_count == "0":
                raise Exception('An error occurred. _ont_count=0 and the line=' + line)

            _ont_data = {}
            _ont_data['ont'] = []
            # get basic info
            i = i + SHIFT - 1
            i = get_basic_info(_ont_count, _ont_data, i, port)

            # get other info
            i = i + SHIFT - 1
            i = getontdata(_ont_count, _ont_data, i)
            jsonConcat(ont_data, _ont_data)
            i = i + 1
        except Exception as e:
            print ("err01")
            print(e)
    return ont_data


def getontdata(_ont_count, _ont_data, i):
    delimiter = " "
    for index in range(0, _ont_count):
        i = i + 1
        try:
            line = lines[i]
            print (line) if isTest else None
            arr = line.split(delimiter)
            # arr = formalize(array=arr)
            arr = list(filter(lambda x: len(x) > 0, arr))
            _ont_data["ont"][index]["datetime"] = get_datetime()
            _ont_data["ont"][index]["description"] = arr[5]
            _ont_data["ont"][index]["sn"] = arr[1]
            _ont_data["ont"][index]["type"] = arr[2]
            _ont_data["ont"][index]["rx"] = -1000
            _ont_data["ont"][index]["tx"] = -1000
            _ont_data["ont"][index]["distance"] = -1
            if _ont_data["ont"][index]["status"] == "online":
                o = arr[4].split('/')
                # print(float(o[0])) if isTest else None
                _ont_data["ont"][index]["rx"] = float(o[0])
                _ont_data["ont"][index]["tx"] = float(o[1])
                _ont_data["ont"][index]["distance"] = arr[3]
        except Exception as e:
            print ("getontdata err")
            print(e)
    return i


def get_basic_info(_ont_count, _ont_data, i, port):
    delimiter = " "
    for index in range(0, _ont_count):
        i = i + 1
        try:
            line = lines[i]
            ont = {}
            arr = line.split(delimiter)
            arr = formalize(arr)
            # print arr
            ont["datetime"] = get_datetime()
            ont["id"] = arr[0]
            ont["port"] = port
            ont["lastuptime"] = arr[2].strip()
            ont["lastdowntime"] = arr[4].strip()
            # ont["lastuptime"] = arr[2] + " " + arr[3]
            # ont["lastdowntime"] = arr[4] + " " + arr[5]
            ont["lastdowncause"] = arr[6]
            if arr[1] == 'online' or arr[1] == 'offline':
                ont["status"] = arr[1]
            else:
                raise Exception('An error occurred. online or offline ?')
            _ont_data["ont"].append(ont)
            # print (ont)
        except Exception as e:
            print ("err03")
            print(e)
    return i


def get_port_number(line):
    keyword = "In port"
    keyword1 = "port"
    delimiter = " "
    port = get_line_value(line=line, delimiter=delimiter, keyword=keyword, keyword1=keyword1).split(',')[0]
    if port:
        return port
    else:
        return ""


def get_ont_count(line):
    delimiter = " "
    try:
        cnt = get_line_value(line=line, delimiter=delimiter, keyword="ONTs are:", keyword1="are:")
        cnt = cnt.replace(" ", "").replace(",", "")
        return int(cnt)
    except Exception as e:
        return 0


def get_datetime():
    return TIMESTAMP


def get_olt_data():
    return all_ont_data


# TODO: time cut, need to restore
def set_datetime(_lines):
    global TIMESTAMP
    t = get_value_from_lines(_lines, "Login  Time", ":")
    TIMESTAMP = t.split(' ')[0]


def get_value_from_lines(_lines, keyword, delimiter):
    for line in _lines:
        if keyword in line:  # this is  the date time got the ONT INFO
            return get_line_value(line, delimiter, keyword, "").strip()
    return ""


def get_line_value(line, delimiter, keyword, keyword1):
    k1 = keyword
    if keyword1:
        k1 = keyword1
    if keyword in line:
        arr = line.split(delimiter)
        for i in range(len(arr)):
            if k1 in arr[i]:
                s = arr[i + 1]
                return arr[i + 1]
    return ""


def checkesIndex():
    e = connect_elasticsearch()
    create_index(e)


if __name__ == '__main__':
    checkesIndex() if isTestES else None
    mins = 15
    while True:
        root_dir = './'
        file_list = [optic_fn for optic_fn in iglob('optics1*.txt') if os.path.isfile(optic_fn)]
        pprint(len(file_list))
        if len(file_list) < 1:
            # print ("waiting for a while ... " + str(datetime.datetime.now()))
            print('No optics file found wait for ' + str(mins) + ' minutes later')
            time.sleep(60 * float(mins))
            continue
        # for f in file_list:
        #     print(f)  # Replace with desired operations
        optic_fn = ""
        output_fn = "optics.json"
        # TODO: read only files not processed. May be write into the database the files status?
        global all_ont_data
        all_ont_data = {}
        all_ont_data['ont'] = []
        with open(output_fn, 'w+') as f:
            # Note that f has now been truncated to 0 bytes, so you'll only
            # be able to read data that you write after this point

            # with open(optic_file_name_json, 'r') as inputfile:
            #     all_ont_data = json.load(inputfile)
            #     jsonConcat(all_ont_data, d)
            optic_fn = file_list[0]
            # first of all, create the first output file with the ont info
            # then other optic files will append to the file
            with open(optic_fn, 'r') as _file:
                # _file = open(optic_file_name, 'r')
                print(optic_fn)
                _file.seek(0)
                lines = _file.readlines()
                set_datetime(lines)
                d = set_olt_data(lines)
                # TODO: send the ont data to the elk
                send2elk(d)
                all_ont_data = jsonConcat(all_ont_data, d)
            # with open(optic_file_name_json, 'w') as outfile:

            json.dump(all_ont_data, f)
            f.close()
            dst = "./output/" + optic_fn
            shutil.move(optic_fn,dst)

            for i in range(1, len(file_list) - 1):
                optic_fn = file_list[i]
                with open(output_fn, 'r') as jsonfile:
                    all_ont_data = json.load(jsonfile)
                with open(optic_fn, 'r') as _file:
                    print(optic_fn)
                    _file.seek(0)
                    lines = _file.readlines()
                    set_datetime(lines)
                    d = set_olt_data(lines)
                    all_ont_data = jsonConcat(all_ont_data, d)
                print (all_ont_data) if isTest else None
                with open(output_fn, 'w') as jsonfile:
                    json.dump(all_ont_data, jsonfile)
                    shutil.move(optic_fn,"./output/" + optic_fn)
