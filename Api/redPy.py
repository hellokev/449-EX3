import redis
r = redis.Redis()
r.mset({"Croatia": "Zagreb", "Bahamas": "Nassau"})
r.get("Bahamas")
print(r.get("Bahamas").decode('utf-8'))