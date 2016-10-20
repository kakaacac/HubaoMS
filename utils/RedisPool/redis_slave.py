# -*- coding: utf-8 -*-
# __author__ = 'billy'


class RedisSlave:
    def __init__(self, sentinel, master_name, socket_timeout=0.1):
        self.sentinel = sentinel
        self.master_name = master_name
        self.socket_timeout = socket_timeout
        pass

    def __get_redis__(self):
        try:
            result = self.sentinel.slave_for(self.master_name, socket_timeout=self.socket_timeout)
            result.ping()
            return result
        except Exception, e:
            print e.__class__, e.message
            raise e

    # KEY COMMANDS
    def dump(self, key):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.dump(key)

    def exists(self, key):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.exists(key)

    def keys(self, pattern='*'):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.keys(pattern)

    def pttl(self, key):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.pttl(key)

    def randomkey(self):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.randomkey()

    def sort(self, key, start=None, num=None, by=None, get=None, desc=False, alpha=False, store=None, groups=False):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.sort(key, start, num, by, get, desc, alpha, store, groups)

    def ttl(self, key):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.ttl(key)

    def type(self, key):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.type(key)

    # STRINGS COMMANDS
    def bitcount(self, key, start=None, end=None):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.bitcount(key, start, end)

    def bitop(self, operation, destkey, *keys):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.bitop(operation, destkey, *keys)

    def get(self, key):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.get(key)

    def getbit(self, key, offset):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.getbit(key, offset)

    def getrange(self, key, start, end):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.scard(key, start, end)

    def mget(self, keys, *args):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.mget(keys, *args)

    def strlen(self, key):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.strlen(key)

    # HASH COMMANDS
    def hexists(self, key, field):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.hexists(key, field)

    def hget(self, key, field):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.hget(key, field)

    def hgetall(self, key):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.hgetall(key)

    def hkeys(self, key):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.hkeys(key)

    def hlen(self, key):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.hlen(key)

    def hmget(self, key, fields, *args):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.hmget(key, fields, *args)

    def hstrlen(self, key, fields):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.execute_command('HSTRLEN', key, fields)

    def hvals(self, key):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.hvals(key)

    # LIST COMMANDS
    def blpop(self, keys, timeout=0):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.blpop(keys, timeout)

    def brpop(self, keys, timeout=0):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.brpop(keys, timeout)

    def brpoplpush(self, source, destination, timeout=0):
        master = self.__get_redis__()
        if master is None:
            return None
        else:
            return master.brpoplpush(source, destination, timeout)

    def lindex(self, key, index):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.lindex(key, index)

    def llen(self, key):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.llen(key)

    def lrange(self, key, start, end):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.lrange(key, start, end)

    # SET COMMANDS
    def scard(self, key):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.scard(key)

    def sdiff(self, keys, *args):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.sdiff(keys, *args)

    def sinter(self, keys, *args):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.sinter(keys, *args)

    def sismember(self, key, member):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.sismember(key, member)

    def smembers(self, key):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.smembers(key)

    def srandmember(self, key, count=None):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            pieces = [key]
            if count:
                pieces.append(count)
            return slave.execute_command('SRANDMEMBER', *pieces)

    def sunion(self, keys, *args):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.sunion(keys, *args)

    def sscan(self, key, cursor=0, match=None, count=None):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.sscan(key, cursor, match, count)

    # SORTED SET COMMANDS
    def zcard(self, key):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.zcard(key)

    def zcount(self, key, min, max):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.zcount(key, min, max)

    def zlexcount(self, key, min, max):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.zlexcount(key, min, max)

    def zrange(self, key, start, stop, withscores=False):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.zrange(key, start, stop, False, withscores)

    def zrangebylex(self, key, min, max, offset=None, count=None):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.zrangebylex(key, min, max, offset, count)

    def zrangebyscore(self, key, min, max, offset=None, count=None, withscores=False):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.zrangebyscore(key, min, max, offset, count, withscores)

    def zrank(self, key, member):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.zrank(key, member)

    def zrevrange(self, key, start, stop, withscores=False):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.zrevrange(key, start, stop, withscores)

    def zrevrangebyscore(self, key, max, min, offset=None, count=None, withscores=False):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.zrevrangebyscore(key, max, min, offset, count, withscores)

    def zrevrank(self, key, member):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.zrevrank(key, member)

    def zscan(self, key, cursor=0, match=None, count=None, score_cast_func=float):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.zscan(key, cursor, match, count, score_cast_func)

    def zscore(self, key, member):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.zscore(key, member)

    def zunionstore(self, destination, keys, aggregate=None):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.zunionstore(destination, keys, aggregate)

    # HyperLogLog COMMANDS
    def pfcount(self, *keys):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.execute_command('PFCOUNT', *keys)

    # GEO COMMANDS
    def geodist(self, key, member1, member2, unit='km'):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.execute_command('GEODIST', key, member1, member2, unit)

    def geohash(self, key, *members):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.execute_command('GEOHASH', key, *members)

    def geopos(self, key, *members):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            return slave.execute_command('GEOPOS', key, *members)

    def georadius(self, key, longitude, latitude, radius, unit='km', withcoord=False, withdist=False, withhash=False, sort=None, count=None):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            pieces = [key, longitude, latitude, radius, unit]
            if withcoord:
                pieces.append('WITHCOORD')
            if withdist:
                pieces.append('WITHDIST')
            if withhash:
                pieces.append('WITHHASH')
            if sort:
                if sort.upper() == 'ASC' or sort.upper() == 'DESC':
                    pieces.append(sort.upper())
            if count:
                pieces.append('COUNT')
                pieces.append(count)
            return slave.execute_command('GEORADIUS', *pieces)

    def georadiusbymember(self, key, member, radius, unit='km', withcoord=False, withdist=False, withhash=False, sort=None, count=None):
        slave = self.__get_redis__()
        if slave is None:
            return None
        else:
            pieces = [key, member, radius, unit]
            if withcoord:
                pieces.append('WITHCOORD')
            if withdist:
                pieces.append('WITHDIST')
            if withhash:
                pieces.append('WITHHASH')
            if sort:
                if sort.upper() == 'ASC' or sort.upper() == 'DESC':
                    pieces.append(sort.upper())
            if count:
                pieces.append('COUNT')
                pieces.append(count)
            return slave.execute_command('GEORADIUSBYMEMBER', *pieces)