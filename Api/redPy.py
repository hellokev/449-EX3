import redis
r = redis.Redis(host='localhost', port=6379)
leaderboard_key = 'players'
top_users = r.zrevrange(leaderboard_key, 0, 4, withscores=True)
for rank, user in enumerate(top_users, start=1):
    username = user[0].decode('utf-8')
    score = user[1]
    print(f"Rank {rank}: {username} - Score: {score}")