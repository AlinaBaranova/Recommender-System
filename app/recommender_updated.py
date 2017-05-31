import networkx as nx
import json
import re
import treetaggerwrapper
from os import path
from nltk.corpus import wordnet
from nltk import word_tokenize
from nltk.corpus import stopwords

# нормализация запроса
tagger = treetaggerwrapper.TreeTagger(TAGLANG='en')

def analyze_query(query):
    stop = stopwords.words('english')

    tokens = word_tokenize(query)
    punct = ',.()":;--&?!\'s'
    tokens = [token for token in tokens if token not in punct]
    tokens = [token for token in tokens if token not in stop]
    
    new_query = ''
    for token in tokens:
        lemma = tagger.tag_text(token)[0].split('\t')[-1]
        new_query += lemma + ' '
    
    return new_query.lower().strip()

# топики для моделей
new_topics = json.loads(open('analyzed_topics.json').read())
# модель с графом
G = nx.read_gexf('topics.gexf')

def sim_graph(word, results_n=10):   
    found_topics = []
    results = []
    recs = set()
    
    for topic in new_topics:
        n = re.search('(\s|^)' + word.lower() + '(\s|$)', topic)
        if n is not None:
            for node_1 in new_topics[topic]:
                for node_2 in G.neighbors(node_1):
                    if node_2 not in recs:
                        n = re.search('(\s|^|\W)' + word.lower() + '(\s|$|\W)', node_2.lower())
                        if n is None:
                            recs.add(node_2)
                            weight = G.edge[node_1][node_2]['weight']
                            results.append([node_2, weight])

    if results != []:
        results = sorted(results, key=lambda x: x[1], reverse=True)[:results_n]
        results = [x[0] for x in results]

    return results

# модель word2vec
model = json.loads(open('model_in_dic.json', 'r').read())
def sim_word2vec(word, results_n=10):
    pos_tags = ['ADJ', 'ADV', 'NOUN', 'PROPN', 'VERB']
    results = []

    for pos_tag in pos_tags:
        word_tagged = word.replace(' ', '::') + '_' + pos_tag
        if word_tagged in model:
            for sim_word in model[word_tagged]:
                sim_word = sim_word.replace('::', '(-| )')
                for topic in new_topics:
                    n = re.search('(\s|^)' + sim_word.lower() + '(\s|$)', topic)
                    if n is not None and word not in topic:
                        result = new_topics[topic] 
                        for r in result:
                            if r not in results:
                                 results.append(r)
                            if len(results) >= results_n:
                                return results

    return results

# модель wordnet
def add_topics(lemma, word, results, results_n):
    for topic in new_topics:
        n = re.search('(\s|^)' + lemma.replace('_', ' ') + '(\s|$)', topic)
        if n is not None:
            m = re.search('(\s|^)' + word.replace('_', ' ') + '(\s|$)', topic)
            if m is None:
                for i in new_topics[topic]:
                    results.add(i)
                if len(results) >= results_n:
                    return results
    return results

def sim_wordnet(word, results_n=10):
    results = set()
    word = word.replace(' ', '_')
    lemmas = set()
    
    for syn in wordnet.synsets(word):
        for synonym in syn.lemmas():
            synonym_name = synonym.name().lower()
            if synonym_name != word and synonym_name not in lemmas:
                lemmas.add(synonym_name)
                results = add_topics(synonym_name, word, results, results_n)
        if len(results) >= results_n:
            return results
        
    lemmas = set()
    for syn in wordnet.synsets(word):
        for synonym in syn.lemmas():
            if synonym.antonyms():
                for antonym in synonym.antonyms():
                    antonym_name = antonym.name().lower()
                    if antonym_name not in lemmas:
                        lemmas.add(antonym_name)
                        results = add_topics(antonym_name, word, results, results_n)
        if len(results) >= results_n:
            return results
    
    lemmas = set()
    for syn in wordnet.synsets(word):
        if syn.hypernyms():
            for hyper in syn.hypernyms():
                for hypernym in hyper.lemmas():
                    hypernym_name = hypernym.name().lower()
                    if hypernym_name not in lemmas:
                        lemmas.add(hypernym_name)
                        results = add_topics(hypernym_name, word, results, results_n)
        if len(results) >= results_n:
            return results
        
    lemmas = set()
    for syn in wordnet.synsets(word):
        if syn.hyponyms():
            for hypo in syn.hyponyms():
                for hyponym in hypo.lemmas():
                    hyponym_name = hyponym.name().lower()
                    if hyponym_name not in lemmas:
                        lemmas.add(hyponym_name)
                        results = add_topics(hyponym_name, word, results, results_n)      
        if len(results) >= results_n:
            return results

    return list(results)

# ссылки
special_char = {'<': '%3C', '>': '%3E', '#': '%23', '%': '%25', '{': '%7B', '}': '%7D', '|': '%7C', '\\': '%5C', 
                '^': '%5E', '~': '%7E', '[': '%5B', ']': '%5D', '`': '%60', ';': '%3B', '/': '%2F', '?': '%3F', 
                ':': '%3A', '@': '%40', '=': '%3D', '&': '%26', '$': '%24', '+': '%2B', '"': '%22', ' ': '%20'}
def right_link(link):
    main_link = 'https://digitalcollections.nypl.org/search/index?filters%5Btopic%5D='
    for i in special_char:
        link = link.replace(i, special_char[i])
    return main_link + link

from flask import Flask, request, render_template, url_for, redirect
app = Flask(__name__)

@app.route('/result/<search>')
def result(search):
    if len(request.args) > 0:
        search = request.args['search']
            
#     results = ["Writing, Hieroglyphic", "Religion", "Egypt", "Inscriptions", "Papyri, Hieratic", "Obelisks",
#                "Study and teaching", "Foreign speakers", "Inscriptions, Greek", "Herbs"]

    query = analyze_query(search)
    results = sim_graph(search)
    if len(results) < 10:
        results += sim_word2vec(search)
    if len(results) < 10:
        results += list(sim_wordnet(search))
        
    new_results = []
    for result in results:
        new_results.append([result, right_link(result)])
    
    if new_results != []:
        return render_template('result.html', search=search, results=new_results)
    
    return render_template('no_results.html', search=search)

@app.route('/')
def index():
    if len(request.args) > 0:
        search = request.args['search']

        return redirect(url_for('result', search=search))
    
    return render_template('index.html')

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/help/')
def help():
    return render_template('help.html')

if __name__ == '__main__':
    app.run()
