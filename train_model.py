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

bins = {}

for doc in e.findall('doc'):
    print 'doc'
    keyword_query = doc.find('keyword_query')
    if keyword_query is None:
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
            passages.append(best_passage_per_link.find('passage').text)
            results.append([link, in_intersection, best_passage_per_link.find('passage').text, score, rank])
        rank += 1
    if (len(passages) <= 3):
        continue
    passages = passage_retrieval.ScorePassages(keyword_query, passages)
    passages.sort(key=lambda tup: tup[1], reverse=True)
    results.sort(key=lambda tup: tup[3],reverse=True)
    top_results = len(results) * 3 / 10
    keywords = passage_retrieval.RemoveSynonymsFromKeywords(keyword_query).split(" AND ")
    index = 1
    success = []
    for result in results:
        # First two features - whether a given passage was in intersection of
        # Google and Bing searches and its rank in Bing search
        new_result = [result[1], result[4]]
        #print new_result

        # Third feature - whether a passage was in wikipedia
        if (result[0].find("wikipedia") != -1):
            new_result.append(1)
        else:
            new_result.append(0)

        # Fourth feature - whether a passage was in yahoo answers
        if (result[0].find("answers.yahoo") != -1):
            new_result.append(1)
        else:
            new_result.append(0)

        # Fifth feature - whether a passage was in yahoo answers
        positions = []
        for keyword in passage_retrieval.stem_tokens(keywords):
            if result[2].find(keyword) != -1:
                positions.append(result[2].find(keyword))

        if (len(positions) == 0):
            break

        # Sixth feature - average distance between query terms
        positions.sort()
        s = 0
        for i in range(1,len(positions)):
            s += positions[i] - positions[i - 1]
        if (len(positions) > 0):
            average_distance = float(s) / len(positions)
        else:
            average_distance = 1000
        new_result.append(average_distance)

        # Seventh feature - number of query terms in passage
        new_result.append(float(len(positions))/len(keywords))

        # Seventh feature - BM25 rank
        index = 1
        for p in passages:
            if (p[0] == result[2]):
                break
            index += 1
        new_result.append(index)

        if (index < top_results):
            Y.append(1)
        else:
            Y.append(0)
        index += 1
        success.append([result[2], result[3], index, model.predict(new_result)[0]])

    min_index = 100
    elem = []
    for s in success:
        if s[2] < min_index and s[3] == '1':
            elem = s
            min_index = s[2]
    if (len(elem) == 0):
        for s in success:
            if s[2] < min_index:
                elem = s
                min_index = s[2]
    b = "1"
    if (len(keywords) >= 6):
        b = "3"
    elif (len(keywords) >= 5):
        b = "2"
    top_score = float(elem[1])
    if b in bins:
        bins[b].append(top_score)
    else:
        bins[b] = [top_score]

for b in bins:
    print b, sum(bins[b])/float(len(bins[b]))
