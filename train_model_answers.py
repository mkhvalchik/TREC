import xml.etree.ElementTree

import numpy as np
import warnings
import machine_learning
import passage_retrieval

warnings.filterwarnings("ignore")

e = xml.etree.ElementTree.parse('output_links_big_bing.xml').getroot()

X = []
Y = []

for doc in e.findall('doc'):
    print 'doc'
    keyword_query = doc.find('keyword_query')
    if keyword_query is None:
        print 'no query'
        continue
    keyword_query = keyword_query.text
    results = []
    passages = []
    rank = 1
    links = doc.find('links')
    for link_passage in links.findall('link_passage'):
        link = link_passage.find("link").text
        in_intersection = link_passage.find("in_intersection").text
        if (in_intersection == "True"):
            in_intersection = True
        else:
            in_intersection = False
        best_passage_per_link = link_passage.find("best_passage_per_link")
        if best_passage_per_link is not None:
            score = float(best_passage_per_link.find('score').text)
            results.append([link, in_intersection, best_passage_per_link.find('passage').text, score, rank])
        rank += 1
    X_1, Y_1 = machine_learning.ComputeAnswerFeatures(keyword_query, results)
    X.extend(X_1)
    Y.extend(Y_1)

model = machine_learning.TrainModel(X, Y)
machine_learning.SaveModel(model, "answers.model")
