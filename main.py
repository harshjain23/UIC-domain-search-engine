from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
import os
import string
import re
import math
import collections
import pandas
from nltk.corpus import stopwords
from nltk import PorterStemmer
from bs4 import BeautifulSoup
import rank

document_text = dict()
index = dict()
q_index = dict()
count = 0
c = 0
doc_len = dict()
q_len = 0
weight = dict()
q_weight = dict()
cos_sim = dict()
ps = PorterStemmer()
final_urls = dict()
pr_scores = dict()
stopwords = set(stopwords.words('english'))
file_path_docs = "C:/Users/harsh/PycharmProjects/IR Project/pages/"
file_path_urls = "C:/Users/harsh/PycharmProjects/IR Project/"


def remove_punctuation(content):
    content = content.strip()
    content = content.lower()
    content = re.sub('\d', '%d', content)
    for x in string.punctuation:
        if x in content:
            content = content.replace(x, " ")
    return content


def stemming(content):
    ps = PorterStemmer()
    words = content.split(" ")
    for word in words:
        content = content.replace(word, ps.stem(word))
    return content


def clean_soup(content):
    for script in content(["script", "style"]):
        script.extract()
    return content.get_text()


def pre_process(content,file):
    content = clean_soup(content)
    content = remove_punctuation(content)
    content = content.replace("\n", " ")
    content = content.replace("\t", " ")
    document_text[file] = content


def build_index(content, file):
    global index
    global document_text
    global stopwords
    for doc_id, text in document_text.items():
        words = text.split(" ")
        for word in words:
            if word not in stopwords:
                if word not in index.keys():
                    index[word] = {}
                    index[word][doc_id] = 1
                elif word in index and doc_id not in index[word].keys():
                    index[word][doc_id] = 1
                else:
                    index[word][doc_id] += 1


def build_q_index(query):
    global q_index
    global stopwords
    words = query.split(" ")
    for word in words:
        if word not in stopwords:
            if word not in q_index.keys():
                q_index[word] = 1
            elif word in q_index:
                q_index[word] = 1
            else:
                q_index[word] += 1


def process_query(query):
    query = query.replace("\n", "")
    query = remove_punctuation(query)
    return query


def calculate_weight():
    global document_text
    global index
    global weight
    global doc_len
    for word in index.keys():
        for doc_id in index[word].keys():
            if word not in weight.keys():
                weight[word] = {}
            tf = (index[word][doc_id])
            idf = math.log((len(document_text) / len(index[word])), 2)
            weight[word][doc_id] = tf * idf
            if doc_id not in doc_len.keys():
                doc_len[doc_id] = (tf**2) * (idf**2)
            else:
                doc_len[doc_id] += (tf**2) * (idf**2)


def calculate_q_weight():
    global q_index
    global q_weight
    global q_len
    global index
    for word in q_index.keys():
        tf = (q_index[word])
        if word in index.keys() and ((len(document_text) / len(index[word]))!=1):
            idf = math.log((len(document_text) / len(index[word])), 2)
        else:
            idf = 0
        if idf != 0:
            q_len += (tf**2) * (idf**2)
        q_weight[word] = tf * idf


def cosine_sim():
    global weight
    global q_weight
    global index
    global q_index
    global cos_sim
    global q_len
    global doc_len
    for word in q_index.keys():
        if word in index.keys():
            for doc_id in index[word].keys():
                if doc_id not in cos_sim.keys():
                    cos_sim[doc_id] = weight[word][doc_id] * q_weight[word] / \
                                            (math.sqrt(doc_len[doc_id]) * math.sqrt(q_len))
                else:
                    cos_sim[doc_id] += weight[word][doc_id] * q_weight[word] / \
                                                 (math.sqrt(doc_len[doc_id]) * math.sqrt(q_len))
    return cos_sim


def get_url(key):
    with open(file_path_urls + 'urlList.txt') as f:
        for i, line in enumerate(f):
            if i == int(key)-1:
                return line


def get_pr_query(pr_scores, query):
    q_words = query.split()
    total_scores = dict()
    for i in q_words:
        for doc in pr_scores.keys():
            total_scores[doc] = 0
            if i in pr_scores[doc].keys():
                total_scores[doc] += pr_scores[doc][i]
    return total_scores


def combine_results(cos_scores, pr_scores):
    combinedScores = dict()
    for k in cos_scores.keys():
        if k in pr_scores.keys():
            combinedScores[k] = 2*(cos_scores[k] * pr_scores[k]) / (cos_scores[k] + pr_scores[k])
    return combinedScores

app = Flask(__name__)


@app.route("/search")
def search():
    global c
    global pr_scores
    for file in os.listdir(file_path_docs):
        print("File Number: " + file)
        f = open(file_path_docs + file, 'rb')
        content = BeautifulSoup(f, 'html.parser')
        pr_scores[file] = rank.pr_vocab(content)
        pre_process(content, file)
    return render_template('test.html')


@app.route("/results", methods=['POST'])
def results():
    global c
    global pr_scores
    if request.method == 'POST':
        global final_urls
        cos_results = dict()
        final_urls_dup = dict()
        pr_results = dict()
        query = request.form['query']
        query = process_query(query)
        build_q_index(query)
        calculate_weight()
        calculate_q_weight()
        cos_results = cosine_sim()
        cos_results = dict(collections.Counter(cos_sim).most_common(c))
        pr_results = get_pr_query(pr_scores, query)
        pr_results = dict(collections.Counter(pr_results).most_common(c))
        final_scores = combine_results(cos_results, pr_results)
        final_scores = dict(collections.Counter(final_scores).most_common(c))
        for key, value in final_scores.items():
            file_name = key.split('.')
            final_urls[file_name[0]] = get_url(file_name[0])
            final_urls_dup[file_name[0]] = get_url(file_name[0])
    return render_template('results.html', **locals())


@app.route('/myredirect/<name>', methods=['GET'])
def myredirect(name):
    print("Reached myredirect method. " + final_urls[name])
    redirect_url = final_urls[name]
    return redirect(redirect_url)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)