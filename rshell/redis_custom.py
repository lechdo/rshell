# -*- coding: utf-8 -*-
"""
Gere l acces a redis
"""
import redis
from rshell.tools.exceptions import RedisError


class RedisCustom:

    def __init__(self, host, port, password, db):
        try:
            self.__connection = redis.Redis(host=host, port=port, password=password, db=db)
            print("Redis connection -> CONNECTED")
        except Exception:
            raise RedisError('Fail to open a REDIS connection')

    @classmethod
    def instance(cls, host, port, password, db):
        """
        Classmethod to fix the autostatement problem in robotframework.
        :param host:
        :param port:
        :param password:
        :param db:
        :return:
        """
        return cls(host, port, password, db)

    def flush_all(self):
        print("Redis flushing all...")
        self.__connection.flushall()
        print("Redis flush all -> SUCCESS")

    def put_key(self, key, value):
        print("Redis append -> key:%s - value:%s" % (key, value))
        self.__connection.append(key=key, value=value)
        print("Redis append -> SUCCESS")

    def put_hash_key(self, hkey, key, value):
        print("Redis put hash key -> hkey:%s - key:%s - value:%s" % (hkey, key, value))
        self.__connection.hset(name=hkey, key=key, value=value)
        print("Redis put hash key -> SUCCESS")

    def control_hash_key(self, hkey, key):
        print("Redis control hash key -> hkey:%s - key:%s" % (hkey, key))
        assert self.__connection.hexists(name=hkey, key=key), "hkey and key doesn't exist!!"
        print("hkey and key exist -> TRUE")
        data = self.__connection.hget(name=hkey, key=key)
        print("BILLING_RUN_DAY (%s - %s) : %s", (hkey, key, data))
