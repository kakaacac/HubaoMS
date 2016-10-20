# -*- coding: utf-8 -*-
from contextlib import contextmanager

from redis_pool import RedisPool

class IntegratedRedis(RedisPool):
    def __init__(self, sentinels=None, master_name=None, password=None, db=None,
                 socket_timeout=None, app=None):
        super(IntegratedRedis, self).__init__(sentinels, master_name, password, db, socket_timeout, app)

    def append(self, key, value):
        return self.master().append(key, value)

    def bitpos(self, key, bit, start=None, end=None):
        return self.master().bitpos(key, bit, start, end)

    def decr(self, key):
        return self.master().decr(key)

    def decrby(self, key, decrement):
        return self.master().decrby(key, decrement)

    def delete(self):
        return self.master().delete()

    def expire(self, key, seconds):
        return self.master().expire(key, seconds)

    def expireat(self, key, timestamp):
        return self.master().expireat(key, timestamp)

    def geoadd(self, key, longitude, latitude, member):
        return self.master().geoadd(key, longitude, latitude, member)

    def getset(self, key, value):
        return self.master().getset(key, value)

    def hdel(self, key):
        return self.master().hdel(key)

    def hincr(self, key, field):
        return self.master().hincr(key, field)

    def hincrby(self, key, field, increment):
        return self.master().hincrby(key, field, increment)

    def hincrbyfloat(self, key, field, increment):
        return self.master().hincrbyfloat(key, field, increment)

    def hmset(self, key, mapping):
        return self.master().hmset(key, mapping)

    def hscan(self, key, cursor=0, match=None, count=None):
        return self.master().hscan(key, cursor, match, count)

    def hset(self, key, field, value):
        return self.master().hset(key, field, value)

    def hsetnx(self, key, field, value):
        return self.master().hsetnx(key, field, value)

    def incr(self, key):
        return self.master().incr(key)

    def incrby(self, key, increment):
        return self.master().incrby(key, increment)

    def incrbyfloat(self, key, increment):
        return self.master().incrbyfloat(key, increment)

    def linsert(self, key, where, pivot, value):
        return self.master().linsert(key, where, pivot, value)

    def lock(self, name, timeout=None, sleep=0.1, blocking_timeout=None, lock_class=None, thread_local=True):
        return self.master().lock(name, timeout, sleep, blocking_timeout, lock_class, thread_local)

    def lpop(self, key):
        return self.master().lpop(key)

    def lpush(self, key):
        return self.master().lpush(key)

    def lpushx(self, key, value):
        return self.master().lpushx(key, value)

    def lrem(self, key, count, value):
        return self.master().lrem(key, count, value)

    def lset(self, key, index, value):
        return self.master().lset(key, index, value)

    def ltrim(self, key, start, end):
        return self.master().ltrim(key, start, end)

    def move(self, key, db):
        return self.master().move(key, db)

    def mset(self):
        return self.master().mset()

    def msetnx(self):
        return self.master().msetnx()

    def persist(self, key):
        return self.master().persist(key)

    def pexpire(self, key, milliseconds):
        return self.master().pexpire(key, milliseconds)

    def pexpireat(self, key, milliseconds_timestamp):
        return self.master().pexpireat(key, milliseconds_timestamp)

    def pfadd(self, key):
        return self.master().pfadd(key)

    def pfmerge(self, destkey):
        return self.master().pfmerge(destkey)

    # Pipeline
    @contextmanager
    def pipeline(self, transaction=True, shard_hint=None):
        master = self.master().__get_redis__()
        p = master.pipeline(transaction, shard_hint)
        yield p
        p.execute()

    def psetex(self, key, milliseconds, value):
        return self.master().psetex(key, milliseconds, value)

    def rename(self, key, newkey):
        return self.master().rename(key, newkey)

    def renamenx(self, key, newkey):
        return self.master().renamenx(key, newkey)

    def restore(self, key, ttl, serialized_value):
        return self.master().restore(key, ttl, serialized_value)

    def rpop(self, key):
        return self.master().rpop(key)

    def rpoplpush(self, source, destination):
        return self.master().rpoplpush(source, destination)

    def rpush(self, key):
        return self.master().rpush(key)

    def rpushx(self, key, value):
        return self.master().rpushx(key, value)

    def sadd(self, key):
        return self.master().sadd(key)

    def sdiffstore(self, destination, keys):
        return self.master().sdiffstore(destination, keys)

    def set(self, key, value, ex=None, px=None, nx=False, xx=False):
        return self.master().set(key, value, ex, px, nx, xx)

    def setbit(self, key, offset, value):
        return self.master().setbit(key, offset, value)

    def setex(self, key, seconds, value):
        return self.master().setex(key, seconds, value)

    def setnx(self, key, value):
        return self.master().setnx(key, value)

    def setrange(self, key, offset, value):
        return self.master().setrange(key, offset, value)

    def sinterstore(self, destination, keys):
        return self.master().sinterstore(destination, keys)

    def smove(self, source, destination, member):
        return self.master().smove(source, destination, member)

    def spop(self, key):
        return self.master().spop(key)

    def srem(self, key):
        return self.master().srem(key)

    def sunionstore(self, destination, keys):
        return self.master().sunionstore(destination, keys)

    def zadd(self, key):
        return self.master().zadd(key)

    def zincr(self, key, member):
        return self.master().zincr(key, member)

    def zincrby(self, key, member, increment):
        return self.master().zincrby(key, member, increment)

    def zinterstore(self, dest, keys, aggregate=None):
        return self.master().zinterstore(dest, keys, aggregate)

    def zrem(self, key):
        return self.master().zrem(key)

    def zremrangebylex(self, key, min, max):
        return self.master().zremrangebylex(key, min, max)

    def zremrangebyrank(self, key, min, max):
        return self.master().zremrangebyrank(key, min, max)

    def zremrangebyscore(self, key, min, max):
        return self.master().zremrangebyscore(key, min, max)

    def bitcount(self, key, start=None, end=None):
        return self.slave().bitcount(key, start, end)

    def bitop(self, operation, destkey):
        return self.slave().bitop(operation, destkey)

    def blpop(self, keys, timeout=0):
        return self.slave().blpop(keys, timeout)

    def brpop(self, keys, timeout=0):
        return self.slave().brpop(keys, timeout)

    def brpoplpush(self, source, destination, timeout=0):
        return self.slave().brpoplpush(source, destination, timeout)

    def dump(self, key):
        return self.slave().dump(key)

    def exists(self, key):
        return self.slave().exists(key)

    def geodist(self, key, member1, member2, unit='km'):
        return self.slave().geodist(key, member1, member2, unit)

    def geohash(self, key):
        return self.slave().geohash(key)

    def geopos(self, key):
        return self.slave().geopos(key)

    def georadius(self, key, longitude, latitude, radius, unit='km', withcoord=False, withdist=False, withhash=False, sort=None, count=None):
        return self.slave().georadius(key, longitude, latitude, radius, unit, withcoord, withdist, withhash, sort, count)

    def georadiusbymember(self, key, member, radius, unit='km', withcoord=False, withdist=False, withhash=False, sort=None, count=None):
        return self.slave().georadiusbymember(key, member, radius, unit, withcoord, withdist, withhash, sort, count)

    def get(self, key):
        return self.slave().get(key)

    def getbit(self, key, offset):
        return self.slave().getbit(key, offset)

    def getrange(self, key, start, end):
        return self.slave().getrange(key, start, end)

    def hexists(self, key, field):
        return self.slave().hexists(key, field)

    def hget(self, key, field):
        return self.slave().hget(key, field)

    def hgetall(self, key):
        return self.slave().hgetall(key)

    def hkeys(self, key):
        return self.slave().hkeys(key)

    def hlen(self, key):
        return self.slave().hlen(key)

    def hmget(self, key, fields):
        return self.slave().hmget(key, fields)

    def hstrlen(self, key, fields):
        return self.slave().hstrlen(key, fields)

    def hvals(self, key):
        return self.slave().hvals(key)

    def keys(self, pattern='*'):
        return self.slave().keys(pattern)

    def lindex(self, key, index):
        return self.slave().lindex(key, index)

    def llen(self, key):
        return self.slave().llen(key)

    def lrange(self, key, start, end):
        return self.slave().lrange(key, start, end)

    def mget(self, keys):
        return self.slave().mget(keys)

    def pfcount(self):
        return self.slave().pfcount()

    def pttl(self, key):
        return self.slave().pttl(key)

    def randomkey(self):
        return self.slave().randomkey()

    def scard(self, key):
        return self.slave().scard(key)

    def sdiff(self, keys):
        return self.slave().sdiff(keys)

    def sinter(self, keys):
        return self.slave().sinter(keys)

    def sismember(self, key, member):
        return self.slave().sismember(key, member)

    def smembers(self, key):
        return self.slave().smembers(key)

    def sort(self, key, start=None, num=None, by=None, get=None, desc=False, alpha=False, store=None, groups=False):
        return self.slave().sort(key, start, num, by, get, desc, alpha, store, groups)

    def srandmember(self, key, count=None):
        return self.slave().srandmember(key, count)

    def sscan(self, key, cursor=0, match=None, count=None):
        return self.slave().sscan(key, cursor, match, count)

    def strlen(self, key):
        return self.slave().strlen(key)

    def sunion(self, keys):
        return self.slave().sunion(keys)

    def ttl(self, key):
        return self.slave().ttl(key)

    def type(self, key):
        return self.slave().type(key)

    def zcard(self, key):
        return self.slave().zcard(key)

    def zcount(self, key, min, max):
        return self.slave().zcount(key, min, max)

    def zlexcount(self, key, min, max):
        return self.slave().zlexcount(key, min, max)

    def zrange(self, key, start, stop, withscores=False):
        return self.slave().zrange(key, start, stop, withscores)

    def zrangebylex(self, key, min, max, offset=None, count=None):
        return self.slave().zrangebylex(key, min, max, offset, count)

    def zrangebyscore(self, key, min, max, offset=None, count=None, withscores=False):
        return self.slave().zrangebyscore(key, min, max, offset, count, withscores)

    def zrank(self, key, member):
        return self.slave().zrank(key, member)

    def zrevrange(self, key, start, stop, withscores=False):
        return self.slave().zrevrange(key, start, stop, withscores)

    def zrevrangebyscore(self, key, max, min, offset=None, count=None, withscores=False):
        return self.slave().zrevrangebyscore(key, max, min, offset, count, withscores)

    def zrevrank(self, key, member):
        return self.slave().zrevrank(key, member)

    def zscan(self, key, cursor=0, match=None, count=None, score_cast_func=float):
        return self.slave().zscan(key, cursor, match, count, score_cast_func)

    def zscore(self, key, member):
        return self.slave().zscore(key, member)

    def zunionstore(self, destination, keys, aggregate=None):
        return self.slave().zunionstore(destination, keys, aggregate)


if __name__ == '__main__':
    pass


