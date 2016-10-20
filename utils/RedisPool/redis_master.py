# -*- coding: utf-8 -*-
# __author__ = 'billy'

from contextlib import contextmanager


class RedisMaster:
    def __init__(self, sentinel, master_name, socket_timeout=0.1):
        self.sentinel = sentinel
        self.master_name = master_name
        self.socket_timeout = socket_timeout
        pass

    def __get_redis__(self):
        try:
            result = self.sentinel.master_for(self.master_name, socket_timeout=self.socket_timeout)
            result.ping()
            return result
        except Exception, e:
            print e.__class__, e.message
            raise

    # KEY COMMANDS
    def delete(self, *keys):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.delete(*keys)

    def expire(self, key, seconds):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.expire(key, seconds)

    def expireat(self, key, timestamp):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.expireat(key, timestamp)

    def move(self, key, db):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.move(key, db)

    def persist(self, key):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.persist(key)

    def pexpire(self, key, milliseconds):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.pexpire(key, milliseconds)

    def pexpireat(self, key, milliseconds_timestamp):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.pexpireat(key, milliseconds_timestamp)

    def rename(self, key, newkey):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.rename(key, newkey)

    def renamenx(self, key, newkey):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.renamenx(key, newkey)

    def restore(self, key, ttl, serialized_value):  # REPLACE
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.restore(key, ttl, serialized_value)

    # STRINGS COMMANDS
    def append(self, key, value):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.append(key, value)

    def bitpos(self, key, bit, start=None, end=None):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.bitpos(key, bit, start, end)

    def decr(self, key):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.decr(key)

    def decrby(self, key, decrement):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.decr(key, decrement)

    def getset(self, key, value):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.getset(key, value)

    def incr(self, key):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.incr(key)

    def incrby(self, key, increment):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.incrby(key, increment)

    def incrbyfloat(self, key, increment):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.incrbyfloat(key, increment)

    def mset(self, *args, **kwargs):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.mset(*args, **kwargs)

    def msetnx(self, *args, **kwargs):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.msetnx(*args, **kwargs)

    def psetex(self, key, milliseconds, value):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.psetex(key, milliseconds, value)

    def set(self, key, value, ex=None, px=None, nx=False, xx=False):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.set(key, value, ex, px, nx, xx)

    def setbit(self, key, offset, value):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.setbit(key, offset, value)

    def setex(self, key, seconds, value):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.setex(key, seconds, value)

    def setnx(self, key, value):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.setnx(key, value)

    def setrange(self, key, offset, value):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.setrange(key, offset, value)

    # HASH COMMANDS
    def hdel(self, key, *fields):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.hdel(key, *fields)

    def hincr(self, key, field):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.hincrby(key, field, 1)

    def hincrby(self, key, field, increment):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.hincrby(key, field, increment)

    def hincrbyfloat(self, key, field, increment):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.hincrbyfloat(key, field, increment)

    def hmset(self, key, mapping):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.hmset(key, mapping)

    def hset(self, key, field, value):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.hset(key, field, value)

    def hsetnx(self, key, field, value):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.hsetnx(key, field, value)

    def hscan(self, key, cursor=0, match=None, count=None):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.hscan(key, cursor, match, count)

    # LIST COMMANDS
    def linsert(self, key, where, pivot, value):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.linsert(key, where, pivot, value)

    def lpop(self, key):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.lpop(key)

    def lpush(self, key, *values):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.lpush(key, *values)

    def lpushx(self, key, value):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.lpushx(key, value)

    def lrem(self, key, count, value):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.lrem(key, count, value)

    def lset(self, key, index, value):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.lset(key, index, value)

    def ltrim(self, key, start, end):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.ltrim(key, start, end)

    def rpop(self, key):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.rpop(key)

    def rpoplpush(self, source, destination):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.rpoplpush(source, destination)

    def rpush(self, key, *values):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.rpush(key, *values)

    def rpushx(self, key, value):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.rpushx(key, value)

    # SET COMMANDS
    def sadd(self, key, *members):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.sadd(key, *members)

    def sdiffstore(self, destination, keys, *args):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.sdiffstore(destination, keys, *args)

    def sinterstore(self, destination, keys, *args):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.sinterstore(destination, keys, *args)

    def smove(self, source, destination, member):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.smove(source, destination, member)

    def spop(self, key):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.spop(key)

    def srem(self, key, *values):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.sunionstore(key, *values)

    def sunionstore(self, destination, keys, *args):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.sunionstore(destination, keys, *args)

    # SORTED SET COMMANDS
    def zadd(self, key, *args, **kwargs):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.zadd(key, *args, **kwargs)

    def zincr(self, key, member):
        return self.zincrby(key, 1, member)

    def zincrby(self, key, member, increment):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.zincrby(key, member, increment)

    def zinterstore(self, dest, keys, aggregate=None):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.zinterstore(dest, keys, aggregate)

    def zrem(self, key, *members):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.zrem(key, *members)

    def zremrangebylex(self, key, min, max):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.zremrangebylex(key, min, max)

    def zremrangebyrank(self, key, min, max):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.zremrangebyrank(key, min, max)

    def zremrangebyscore(self, key, min, max):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.zremrangebyscore(key, min, max)

    # HyperLogLog COMMANDS
    def pfadd(self, key, *elements):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.pfadd(key, *elements)

    def pfmerge(self, destkey, *sourcekeys):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.pfmerge(destkey, *sourcekeys)

    # GEO COMMANDS
    def geoadd(self, key, longitude, latitude, member):#, *args, **kwargs
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.execute_command('GEOADD', key, longitude, latitude, member)

    # Pipeline
    @contextmanager
    def pipeline(self, transaction=True, shard_hint=None):
        master = self.__get_redis__()
        p = master.pipeline(transaction, shard_hint)
        yield p
        p.execute()

    # Lock
    def lock(self, name, timeout=None, sleep=0.1, blocking_timeout=None,
             lock_class=None, thread_local=True):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.lock(name, timeout, sleep, blocking_timeout, lock_class, thread_local)