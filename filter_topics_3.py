import os
import json

def filled_topics():
    with_topics = 0
    all_items = 0
    col_with_topics = 0
    all_col = 0
    new_path = './filled_topics'
    old_path = './topics'
    
    if not os.path.exists(new_path):
        os.makedirs(new_path)
        
    for root, dirs, files in os.walk(old_path):
        for file in files:
            if file.startswith('items_'):
                print(file)
                all_col += 1
                topics = {}
                items = json.loads(open(os.path.join(old_path, file), 'r').read())
                all_items += len(items)
                for item in items:
                    if items[item] != []:
                        topics[item] = items[item]
                        with_topics += 1
                if topics != {}:
                    col_with_topics += 1
                    with open(os.path.join(new_path, file.replace('items_', 'topics_')), 'w') as outfile:
                        json.dump(topics, outfile)
    print(with_topics, all_items)
    print(col_with_topics, all_col)

##filled_topics()

def filter_topics():
    path = './filled_topics'

    for root, dirs, files in os.walk(path):
        for file in files:
            print(file)
            new_collection = {}
            f = open(os.path.join(path, file), 'r+')
            collection = json.loads(f.read())
            for item in collection:
                topics = set()
                for topic in collection[item]:
                    if type(topic) is list:
                        for part in topic:
                            topics.add(part)
                    else:
                        topics.add(topic)
                new_collection[item] = list(topics)
            f.seek(0)
            json.dump(new_collection, f)
            f.truncate()
            f.close()

filter_topics()
