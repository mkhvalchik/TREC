import requests

r = requests.post("http://ec2-52-207-219-237.compute-1.amazonaws.com:11000", data={'qid': 12345, 'title': 'some question', 'body': 'how to feed a cat', 'category': 'cats'})

print r.text
