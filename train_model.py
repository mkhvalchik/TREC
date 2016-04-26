import pprint
import xml.etree.ElementTree
from xml.sax.saxutils import escape
from googleapiclient.discovery import build
import common_lib
import passage_retrieval

e = xml.etree.ElementTree.parse('output_links_big_bing.xml').getroot()

X = []
Y = []

for ves in e.findall('data'):
    for doc in ves.findall('doc'):
        keyword_query = doc.find('keyword_query').text
        results = []
        rank = 1
        for link_passage in doc.findall('link_passage'):
            link = link_passage.find("link").text
            in_intersection = link_passage.find("in_intersection").text
            if (in_intersection == "True"):
                in_intersection = True
            else:
                in_intersection = False
            best_passage_per_link = link_passage.find("best_passage_per_link")
            passage = best_passage_per_link.find("passage").text
            if passage:
                score = int(best_passage_per_link.find("passage").text)
                results.append([link, in_intersection, passage, score, rank, 0])
            rank += 1
        results.sort(key=lambda tup: tup[3])
        top_results = len(results) * 4 / 5
        keywords = RemoveSynonymsFromKeywords(keyword_query).split(" AND ")
        index = 1
        for result in results:
            if (result[0].find("wikipedia") != -1):
                result.append(1)
            else:
                result.append(0)
            if (result[0].find("answers.yahoo") != -1):
                result.append(1)
            else:
                result.append(0)
            positions = []
            for keyword in stem_tokens(keywords):
                if passage.find(keyword) != -1:
                    positions.append(passage.find(keyword))
            results.sort(positions)
            s = 0
            for i in range(1:len(positions)):
                s += positions[i] - positions[i - 1]
            if (len(positions) > 0):
                average_distance = float(s) / len(positions)
            else:
                average_distance = 1000
            result.append(average_distance)
            if (index >= top_results):
                y.append(1)
            else:
                y.append(0)
            index += 1
            print result
            print y
            X.append(result)

clf = svm.SVC()
clf.fit(X, y)
