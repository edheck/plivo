from time import time


class RateLimitExceededException(Exception):
    def __init__(self, message):
        super(RateLimitExceededException, self).__init__(message)


class APIRateLimiter(object):

    _DAY_MILLIS = 86400000
    _MAX_CALLS_PER_DAY = 50

    def __init__(self, redis_client):
        """

        :param redis.Redis redis_client:
        :return:
        """
        self.redis_client = redis_client

    def _ratelimit(self, from_number, current_timestamp):
        """

        :param str from_number:
        :param int current_timestamp:
        :return:
        """

        pipeline = self.redis_client.pipeline()
        try:
            timestamps = [int(x) for x in self.redis_client.smembers(from_number)]
            to_del_timestamps = \
                [x for x in timestamps if x + APIRateLimiter._DAY_MILLIS < current_timestamp]
            for timestamp in to_del_timestamps:
                pipeline.srem(from_number, timestamp)
            remaining = len(timestamps) - len(to_del_timestamps)
            to_add_timestamp = None
            if remaining < APIRateLimiter._MAX_CALLS_PER_DAY:
                to_add_timestamp = current_timestamp
            else:
                raise RateLimitExceededException(message="limit reached for from %s" % from_number)
            if to_add_timestamp:
                pipeline.sadd(from_number, to_add_timestamp)
        finally:
            pipeline.execute()

    def ratelimit(self, from_number):
        """

        :param str from_number:
        :return:
        """
        current_timestamp = int(time() * 1000)
        self._ratelimit(from_number=from_number, current_timestamp=current_timestamp)
