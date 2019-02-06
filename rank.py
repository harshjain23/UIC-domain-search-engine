import os
import re
import string
import collections
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
import nltk
import nltk.tokenize
import pagerank


s1 = set(stopwords.words('english'))


def clean_soup(content):
    for script in content(["script", "style"]):
        script.extract()
    return content.get_text()


def pos_tag(words):
    return [pair[1] for pair in nltk.pos_tag(words)]


def tokenize_words(sentence):
    return nltk.tokenize.word_tokenize(sentence)


def remove_punctuation(content):
    content = content.strip()
    content = content.lower()
    content = re.sub('\d', '%d', content)
    for x in string.punctuation:
        if x in content:
            content = content.replace(x, " ")
    return content


def process_document(document, posTags):
    filteredWords = []
    global s1
    document = clean_soup(document)
    document = remove_punctuation(document)
    document = document.replace("\n", " ")
    document = document.replace("\t", " ")
    words = tokenize_words(document)
    posTags = pos_tag(words)
    for index, word in enumerate(words):
        tag = posTags[index]
        if tag in posTags and word not in s1:
            filteredWords.append(word)
    return filteredWords


def pr_vocab(document):
    windowSize = 2
    posTags = ['NN', 'NNS', 'NNP', 'NNPS', 'JJ']
    words = process_document(document, posTags)
    edge = collections.defaultdict(lambda: collections.Counter())
    for index, word in enumerate(words):
        for otherIndex in range(index - windowSize, index + windowSize + 1):
            if otherIndex >= 0 and otherIndex < len(words) and otherIndex != index:
                otherWord = words[otherIndex]
                edge[word][otherWord] += 1.0
    wordProbabilities = pagerank.apply_p_rank(edge)
    return wordProbabilities.to_dict()

