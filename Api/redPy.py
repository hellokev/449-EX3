import redis

r = redis.Redis()
r.mset({"Croatia": "Zagreb", "Bahamas": "Nassau"})
result = r.get("Bahamas")

print(result.decode('utf-8'))
