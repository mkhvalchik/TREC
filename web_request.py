import requests

r = requests.post("http://172.31.62.84:11000", data={'qid': 12345, 'title': 'some question', 'body': 'how to feed a cat', 'category': 'cats'})

print r.text
