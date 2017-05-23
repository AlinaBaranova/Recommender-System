import requests
import json
import math
import os
import time

# добавляет топики элемента в словарь
def add_item(item):
##    global num_items
    global items
    global errors
##    print('item', item['apiUri'])
##    num_items += 1
    items[item['uuid']] = []
    if 'subject' in item['mods']:
        
        # может быть словарём или массивом (см. вложенные коллекции) 
        if type(item['mods']['subject']) is dict:
            if 'topic' in item['mods']['subject']:
                  items[item['uuid']].append(item['mods']['subject']['topic'])
                  
                  # на всякий случай, если снова столкнёмся со словарём
##                if type(item['mods']['subject']['topic']) is dict:
##                    items[item['uuid']].append(item['mods']['subject']['topic']['$'])
##                else:
##                    items[item['uuid']].append(item['mods']['subject']['topic'])
        else:
            for subject in item['mods']['subject']:
                if 'topic' in subject:
                    
                    # может быть словарём или массивом (см. вложенные коллекции)
                    if type(subject['topic']) is dict:
                        items[item['uuid']].append(subject['topic']['$'])
                    else:
                        items[item['uuid']].append(subject['topic'])
                        
##    if items[item['uuid']] == []:
##        errors.append(item)

# при помощи add_item извлекает топики из коллекций (прежде всего, из корневых)
def extract_topics(url_col_init, page):
    global auth
##    global num_items
##    global all_items
    
    # достаёт коллекцию
    call = requests.get(url_col_init, headers={'Authorization': auth})
    collection_init = json.loads(call.text)['nyplAPI']['response']
    
    # если есть вложенные коллекции, рекурсивно вызывает функцию для них
    if 'collection' in collection_init:
        
        # если вложенная коллекция одна, то она представлена в формате словаря; в случае многих коллекций используется массив
        if type(collection_init['collection']) is dict:
##            all_items += num_items
##            num_items = 0
##            print('collection', collection_init['collection']['levelUri'])
##            call_for_items = requests.get(collection_init['collection']['levelUri'], headers={'Authorization': auth})
##            print('numItems', json.loads(call_for_items.text)['nyplAPI']['response']['numItems'])
            try:
                extract_topics(collection_init['collection']['levelUri'], 0)
            except:
                time.sleep(5)
                extract_topics(collection_init['collection']['levelUri'], 0)
##            print('found', num_items)
        else:
            for collection in collection_init['collection']:
##                all_items += num_items
##                num_items = 0
##                print('collection', collection['levelUri'])
##                call_for_items = requests.get(collection['levelUri'], headers={'Authorization': auth})
##                print('numItems', json.loads(call_for_items.text)['nyplAPI']['response']['numItems'])
                try:
                    extract_topics(collection['levelUri'], 0)
                except:
                    time.sleep(5)
                    extract_topics(collection['levelUri'], 0)
##                print('found', num_items)
                
    # если есть элементы, для них вызывается функция add_item
    if 'item' in collection_init:
        
        # может быть словарём или массивом (см. вложенные коллекции)
        if type(collection_init['item']) is dict:
            add_item(collection_init['item'])
        else:
            for item in collection_init['item']:
                add_item(item)
                
    # если страниц несколько, перебирает их все и рекурсивно вызывает функцию от каждой
    # (по умолчанию на странице отображается 10 элементов/коллекций)
    num_results = int(collection_init['numResults'])
    if page == 0 and num_results > 10:
        for i in range(2, math.ceil(num_results/10)+1):
##            print('page ' + str(i))
            try:
                extract_topics(url_col_init + '?page=' + str(i), i)
            except:
                time.sleep(5)
                extract_topics(url_col_init + '?page=' + str(i), i)

# основная функция; с помощью двух других извлекает топики; записывает в файл в папке "topics" с названием вида
# "items_UUID-COLLECTION"
def parse_root_collections():
    uuids_col = json.loads(open('all_cols_uuids.json').read())
    uuids_col = ['d6d29460-031a-0133-7ddc-58d385a7b928']
    
    url_col = 'http://api.repo.nypl.org/api/v1/collections/'
    global auth
    global items
    global errors
##    global all_items

    # создаёт папку "topics", если её нет
    folder = './topics'
    if not os.path.exists(folder):
        os.makedirs(folder)

    # перебирает корневые коллекции; для каждой коллекции создаёт файл с топиками
    for uuid_col in uuids_col:
        print('ROOT COLLECTION', uuid_col)
        try:
            extract_topics(url_col + uuid_col, 0)
        except:
            time.sleep(5)
            extract_topics(url_col + uuid_col, 0)

##        print('Should be extracted at least:', all_items)
##        print('Extracted:', len(items))
##        call_for_items = requests.get(url_col + uuid_col, headers={'Authorization': auth})
##        print('In the root collection should be:', json.loads(call_for_items.text)['nyplAPI']['response']['numItems'])
        
        with open(os.path.join(folder, 'items_' + uuid_col + '.json'), 'w') as outfile:
            json.dump(items, outfile)

        items = {}
        errors = []

errors = []
items = {}
##num_items = 0
##all_items = 0
auth = 'Token token=avgeck6iayd42klx'

parse_root_collections()
