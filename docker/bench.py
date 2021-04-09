import timeit

print("res:"+str(timeit.timeit('import json; json.dumps(list(range(10000)))', number=5000)))