import requests

r = requests.post("http://ec2-54-164-37-93.compute-1.amazonaws.com:11000", data={'qid': 12345, 'title': 'some question', 'body': 'Hello', 'category': 'cats'})

print r.text
