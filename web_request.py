import requests
import sys


r = requests.post("http://ec2-52-207-219-237.compute-1.amazonaws.com:11000", data={'qid': 12345, 'title': sys.argv[1], 'body': sys.argv[1], 'category': 'cats'})

print r.text
