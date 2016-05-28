import passage_retrieval
from sklearn import svm
import pickle
import math

# Computes features for the answer selection ML model
def ComputeAnswerFeatures(keyword_query, results):
    X = []
    Y = []
    passages = []
    for r in results:
        passages.append(r[2])
    passages = passage_retrieval.ScorePassages(keyword_query, passages)
    passages.sort(key=lambda tup: tup[1], reverse=True)
    results.sort(key=lambda tup: tup[3],reverse=True)
    top_results = len(results) / 3
    keywords = passage_retrieval.RemoveSynonymsFromKeywords(keyword_query).split(" AND ")
    index = 1
    for result in results:
        # First two features - whether a given passage was in intersection of
        # Google and Bing searches and its rank in Bing search
        new_result = [result[1], result[4]]

        # Third feature - whether a passage was in wikipedia
        if (result[0].lower().find("wikipedia") != -1):
            new_result.append(1)
        else:
            new_result.append(0)

        # Fourth feature - whether a passage was in yahoo answers
        if (result[0].lower().find("answers.yahoo") != -1):
            new_result.append(1)
        else:
            new_result.append(0)

        # Fifth feature - whether a passage was in yahoo answers
        positions = []
        for keyword in passage_retrieval.stem_tokens(keywords):
            keyword = keyword.lower()
            if result[2].lower().find(keyword) != -1:
                positions.append(result[2].lower().find(keyword))

        if (len(positions) == 0):
            continue

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

        # eighth feature - BM25 rank
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
        X.append(new_result)
    return X, Y

# Computes features for the passage selection ML model
def ComputePassageFeatures(keyword_query, results):
    top_results = results
    top_results.sort(key=lambda tup: tup[2], reverse=True)
    top_results = top_results[:(len(top_results) / 3)]
    results.sort(key=lambda tup: tup[1], reverse=True)
    keywords = passage_retrieval.RemoveSynonymsFromKeywords(keyword_query).split(" AND ")

    X = []
    Y = []

    rank = 0
    for result in results:
        rank += 1
        features = []

        # First feature - BM5 rank
        features.append(rank)

        positions = []
        for keyword in passage_retrieval.stem_tokens(keywords):
            keyword = keyword.lower()
            if result[0].lower().find(keyword) != -1:
                positions.append(result[0].lower().find(keyword))

        if (len(positions) == 0):
            continue

        # Second feature - average distance between query terms
        positions.sort()
        s = 0
        for i in range(1,len(positions)):
            s += positions[i] - positions[i - 1]
        if (len(positions) > 0):
            average_distance = float(s) / len(positions)
        else:
            average_distance = 1000
        features.append(math.ceil(average_distance / 10))

        # Third feature - number of query terms in passage
        features.append(float(len(positions))/len(keywords))

        # Fourth feature - number of words in passage
        features.append(len(result[0].split(" ")) / 10)

        label = 0
        for top_result in top_results:
            if result[0] == top_result[0]:
              label = 1

        if label == 1 and average_distance == 0.0:
            continue

        X.append(features)
        Y.append(label)
    return X, Y

def TrainModel(X, Y):
    clf = svm.SVC()
    clf.fit(X, Y)
    return clf

def Predict(model, X):
    return model.predict(X)

def SaveModel(model, filename):
    pickle.dump(model, open(filename, "wb" ))

def LoadModel(filename):
    return pickle.load(open(filename, "rb"))
