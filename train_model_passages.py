import xml.etree.ElementTree

import numpy as np
import warnings
import machine_learning
import passage_retrieval

warnings.filterwarnings("ignore")

e = xml.etree.ElementTree.parse('output_passages_big_bing.xml').getroot()

X = []
Y = []

for doc in e.findall('doc'):
    print 'doc'
    keyword_query = doc.find('keyword_query')
    if keyword_query is None:
        print 'no query'
        continue
    keyword_query = keyword_query.text
    for link in doc.findall('link'):
        i = 0
        results = []
        for passage in link.findall('passage'):
            passage_text = passage.find("text").text
            passage_score = float(passage.find("score").text)
            top_answer_similarity = float(passage.find("top_answer_similarity").text)
            results.append([passage_text, passage_score, top_answer_similarity])
            i += 1
            if i > 20:
                break
        count_null = 0
        for result in results:
            if (result[2] != 0):
                count_null += 1
        if (count_null >= float(4) * len(results)/5):
            continue
        X_1, Y_1 = machine_learning.ComputePassageFeatures(keyword_query, results)
        X.extend(X_1)
        Y.extend(Y_1)

print X, Y

model = machine_learning.TrainModel(X, Y)
machine_learning.SaveModel(model, "passages.model")
