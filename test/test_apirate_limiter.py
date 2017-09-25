import unittest
from time import time

from apirate_limiter import APIRateLimiter, RateLimitExceededException
from mock.mock import MagicMock


class TestAPIRateLimiter(unittest.TestCase):

    def setUp(self):
        redis_client = MagicMock()
        self.apirate_limiter = APIRateLimiter(redis_client=redis_client)

    def test_ratelimit_from_number_first_time(self):
        current_timestamp = int(time()*1000)
        from_number = '9740171794'
        self.apirate_limiter.redis_client.smembers.return_value = set()
        self.apirate_limiter.redis_client.pipeline.return_value = redis_pipeline_mock = MagicMock()
        self.apirate_limiter._ratelimit(from_number, current_timestamp)
        self.assertEquals(self.apirate_limiter.redis_client.smembers.call_count, 1)
        self.apirate_limiter.redis_client.smembers.assert_called_with(from_number)
        self.assertEquals(redis_pipeline_mock.srem.call_count, 0)
        self.assertEquals(redis_pipeline_mock.sadd.call_count, 1)
        redis_pipeline_mock.sadd.assert_called_with(from_number, current_timestamp)
        self.assertEquals(redis_pipeline_mock.execute.call_count, 1)

    def test_ratelimit_from_number_not_execeeded(self):
        current_timestamp = int(time()*1000)
        from_number = '9740171794'
        self.apirate_limiter.redis_client.smembers.return_value = set([current_timestamp-10])
        self.apirate_limiter.redis_client.pipeline.return_value = redis_pipeline_mock = MagicMock()
        self.apirate_limiter._ratelimit(from_number, current_timestamp)
        self.assertEquals(self.apirate_limiter.redis_client.smembers.call_count, 1)
        self.apirate_limiter.redis_client.smembers.assert_called_with(from_number)
        self.assertEquals(redis_pipeline_mock.srem.call_count, 0)
        self.assertEquals(redis_pipeline_mock.sadd.call_count, 1)
        redis_pipeline_mock.sadd.assert_called_with(from_number, current_timestamp)
        self.assertEquals(redis_pipeline_mock.execute.call_count, 1)

    def test_ratelimit_from_number_exceeded(self):
        current_timestamp = int(time()*1000)
        from_number = '9740171794'
        timestamps = [current_timestamp - x for x in xrange(1, 51)]
        self.apirate_limiter.redis_client.smembers.return_value = set(timestamps)
        self.apirate_limiter.redis_client.pipeline.return_value = redis_pipeline_mock = MagicMock()
        try:
            self.apirate_limiter._ratelimit(from_number, current_timestamp)
        except RateLimitExceededException as rle:
            self.assertEquals(rle.message, 'limit reached for from %s' % from_number)
        self.assertEquals(self.apirate_limiter.redis_client.smembers.call_count, 1)
        self.apirate_limiter.redis_client.smembers.assert_called_with(from_number)
        self.assertEquals(redis_pipeline_mock.srem.call_count, 0)
        self.assertEquals(redis_pipeline_mock.execute.call_count, 1)

    def test_ratelimit_from_number_exceeded_2(self):
        current_timestamp = int(time()*1000)
        from_number = '9740171794'
        timestamps = [current_timestamp - x for x in xrange(1, 51)]
        timestamps.extend([current_timestamp - self.apirate_limiter._DAY_MILLIS - 1])
        self.apirate_limiter.redis_client.smembers.return_value = set(timestamps)
        self.apirate_limiter.redis_client.pipeline.return_value = redis_pipeline_mock = MagicMock()
        try:
            self.apirate_limiter._ratelimit(from_number, current_timestamp)
        except RateLimitExceededException as rle:
            self.assertEquals(rle.message, 'limit reached for from %s' % from_number)
        self.assertEquals(self.apirate_limiter.redis_client.smembers.call_count, 1)
        self.apirate_limiter.redis_client.smembers.assert_called_with(from_number)
        self.assertEquals(redis_pipeline_mock.srem.call_count, 1)
        redis_pipeline_mock.srem.assert_called_with(from_number, current_timestamp - self.apirate_limiter._DAY_MILLIS - 1)
        self.assertEquals(redis_pipeline_mock.execute.call_count, 1)
