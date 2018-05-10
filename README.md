### REDIS PARSER 
A simple redis resp protocol parser written with python.

inspired by [lua-resty-redis](https://github.com/openresty/lua-redis-parser)

### example
```
[aidu35@aidu35 py]$ python redis_cli.py 
redis-cli> SET name gerrard EX 10
OK
redis-cli> HGETALL name
WRONGTYPE Operation against a key holding the wrong kind of value
redis-cli> TTL name
10
redis-cli> GET name
gerrard
redis-cli> KEYS *
website
苏州
weather
name
```

### RESP definition
[REdis Serialization Protocol](https://redis.io/topics/protocol)

