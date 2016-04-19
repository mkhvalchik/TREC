from py_bing_search import PyBingSearch

bing = PyBingSearch('3Bybyj2qcK/w5FXbBqBUjI9MajN51efC2uYldmzvvnY')
result_list = bing.search_all("(yawn) AND (other OR early) AND (people) AND (contagious OR catching) AND (room)", limit=50, format='json')

print [result.url for result in result_list][:10]
