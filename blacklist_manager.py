from time import time


class BlacklistManager(object):

    _REDIS_BLACKLIST_HASH = 'blacklisted'
    _FOUR_HOURS = 4 * 3600000 # ms
    _REDIS_BLACKLIST_HASH_KEY_FMT = '%s-%s'

    def __init__(self, redis_client):
        """

        :param redis.Redis redis_client:
        :return:
        """
        self.redis_client = redis_client

    def _blacklist(self, from_number, to_number, current_timestamp):
        """

        :param str from_number:
        :param str to_number:
        :param int current_timestamp:
        :return:
        """
        from_to_pair = BlacklistManager._REDIS_BLACKLIST_HASH_KEY_FMT % (from_number, to_number)
        blacklist_start_timestamp = \
            self.redis_client.hget(BlacklistManager._REDIS_BLACKLIST_HASH, from_to_pair)
        if blacklist_start_timestamp is None:
            self.redis_client.hset(BlacklistManager._REDIS_BLACKLIST_HASH, from_to_pair,
                                   current_timestamp)
        else:
            if int(blacklist_start_timestamp) + BlacklistManager._FOUR_HOURS <= current_timestamp:
                self.redis_client.hset(BlacklistManager._REDIS_BLACKLIST_HASH, from_to_pair, current_timestamp)

    def blacklist(self, from_number, to_number):
        """

        :param str from_number:
        :param str to_number:
        :return:
        """
        current_timestamp = int(time() * 1000)
        return self._blacklist(from_number=from_number, to_number=to_number,
                               current_timestamp=current_timestamp)

    def _check_blacklist(self, from_number, to_number, current_timestamp):
        """

        :param str from_number:
        :param str to_number:
        :param int current_timestamp:
        :return:
        """
        from_to_pair = BlacklistManager._REDIS_BLACKLIST_HASH_KEY_FMT % (from_number, to_number)
        blacklist_start_timestamp = \
            self.redis_client.hget(BlacklistManager._REDIS_BLACKLIST_HASH, from_to_pair)
        if blacklist_start_timestamp is not None and \
            int(blacklist_start_timestamp) + BlacklistManager._FOUR_HOURS >= current_timestamp:
                return True
        return False

    def check_blacklist(self, from_number, to_number):
        """

        :param str from_number:
        :param str to_number:
        :return:
        """
        current_timestamp = int(time() * 1000)
        return self._check_blacklist(from_number=from_number, to_number=to_number,
                                     current_timestamp=current_timestamp)



