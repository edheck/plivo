import unittest
from time import time

from blacklist_manager import BlacklistManager
from mock.mock import MagicMock


class TestBlacklistManager(unittest.TestCase):

    def setUp(self):
        redis_client = MagicMock()
        self.blacklist_manager = BlacklistManager(redis_client=redis_client)

    def test_blacklist_first_time(self):
        from_number = '9740171794'
        to_number = '9740171795'
        current_timestamp = int(time()*1000)
        self.blacklist_manager.redis_client.hget.return_value = None
        self.blacklist_manager._blacklist(from_number, to_number, current_timestamp)
        self.assertEquals(self.blacklist_manager.redis_client.hset.call_count, 1)
        self.blacklist_manager.redis_client.hset.assert_called_with(
            self.blacklist_manager._REDIS_BLACKLIST_HASH,
            self.blacklist_manager._REDIS_BLACKLIST_HASH_KEY_FMT % (from_number, to_number),
            current_timestamp)

    def test_blacklist_expired(self):
        from_number = '9740171794'
        to_number = '9740171795'
        current_timestamp = int(time()*1000)
        self.blacklist_manager.redis_client.hget.return_value = current_timestamp - (self.blacklist_manager._FOUR_HOURS + 1)
        self.blacklist_manager._blacklist(from_number, to_number, current_timestamp)
        self.assertEquals(self.blacklist_manager.redis_client.hset.call_count, 1)
        self.blacklist_manager.redis_client.hset.assert_called_with(
            self.blacklist_manager._REDIS_BLACKLIST_HASH,
            self.blacklist_manager._REDIS_BLACKLIST_HASH_KEY_FMT % (from_number, to_number),
            current_timestamp)

    def test_blacklist_not_expired(self):
        from_number = '9740171794'
        to_number = '9740171795'
        current_timestamp = int(time()*1000)
        self.blacklist_manager.redis_client.hget.return_value = current_timestamp - (self.blacklist_manager._FOUR_HOURS - 1)
        self.blacklist_manager._blacklist(from_number, to_number, current_timestamp)
        self.assertEquals(self.blacklist_manager.redis_client.hset.call_count, 0)

    def test_check_blacklist_true(self):
        from_number = '9740171794'
        to_number = '9740171795'
        current_timestamp = int(time()*1000)
        self.blacklist_manager.redis_client.hget.return_value = current_timestamp - (self.blacklist_manager._FOUR_HOURS - 1)
        is_blacklisted = self.blacklist_manager._check_blacklist(from_number, to_number, current_timestamp)
        self.assertTrue(is_blacklisted)
        self.assertEquals(self.blacklist_manager.redis_client.hget.call_count, 1)
        self.blacklist_manager.redis_client.hget.assert_called_with(
            self.blacklist_manager._REDIS_BLACKLIST_HASH,
            self.blacklist_manager._REDIS_BLACKLIST_HASH_KEY_FMT % (from_number, to_number))

    def test_check_blacklist_missing(self):
        from_number = '9740171794'
        to_number = '9740171795'
        current_timestamp = int(time()*1000)
        self.blacklist_manager.redis_client.hget.return_value = None
        is_blacklisted = self.blacklist_manager._check_blacklist(from_number, to_number, current_timestamp)
        self.assertFalse(is_blacklisted)
        self.assertEquals(self.blacklist_manager.redis_client.hget.call_count, 1)
        self.blacklist_manager.redis_client.hget.assert_called_with(
            self.blacklist_manager._REDIS_BLACKLIST_HASH,
            self.blacklist_manager._REDIS_BLACKLIST_HASH_KEY_FMT % (from_number, to_number))

    def test_check_blacklist_expired(self):
        from_number = '9740171794'
        to_number = '9740171795'
        current_timestamp = int(time()*1000)
        self.blacklist_manager.redis_client.hget.return_value = current_timestamp - (self.blacklist_manager._FOUR_HOURS + 1)
        is_blacklisted = self.blacklist_manager._check_blacklist(from_number, to_number, current_timestamp)
        self.assertFalse(is_blacklisted)
        self.assertEquals(self.blacklist_manager.redis_client.hget.call_count, 1)
        self.blacklist_manager.redis_client.hget.assert_called_with(
            self.blacklist_manager._REDIS_BLACKLIST_HASH,
            self.blacklist_manager._REDIS_BLACKLIST_HASH_KEY_FMT % (from_number, to_number))


