import json
import time
import calendar

data = {}
data['ont'] = []
data['ont'].append({
    'datetime': calendar.timegm(time.gmtime()),
    'port': '0/0/0',
    'ontnum': '765',
    'description': ""
})
data['ont'].append({
    'datetime': calendar.timegm(time.gmtime()),
    'port': '0/0/0',
    'ontnum': '322',
    'description': "test2"
})
data['ont'].append({
    'datetime': calendar.timegm(time.gmtime()),
    'port': '0/0/0',
    'ontnum': '4326',
    'description': "test3"
})
with open('data.json', 'w') as outfile:
    json.dump(data, outfile)

with open('data.json') as json_file:
    data = json.load(json_file)
    for p in data['ont']:
        print('datetime: ' + str(p['datetime']))
        print('port number: ' + p['port'])
        print('ont number: ' + p['ontnum'])
        print('ont desc: ' + p['description'])
        print('')
