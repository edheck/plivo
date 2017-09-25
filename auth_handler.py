from models import Account, PhoneNumber


class AuthHandler(object):

    _REDIS_AUTH_HASH = 'auth'

    def __init__(self, redis_client, db_handler):
        """

        :param redis.Redis redis_client:
        :param PostgresDBHandler db_handler:
        :return:
        """
        self.redis_client = redis_client
        self.db_handler = db_handler

    def _check_auth(self, username, auth_id, db_session):
        """

        :param str username:
        :param str auth_id:
        :param sqlalchemy.orm.session.Session db_session:
        :return: tuple of (bool, str) indicating valid auth and phone num
        :rtype: tuple
        """
        cached_auth_id = self.redis_client.hget(AuthHandler._REDIS_AUTH_HASH, username)
        if cached_auth_id is None:
            account_phonenum = \
                db_session.query(Account,PhoneNumber). \
                    join(PhoneNumber, PhoneNumber.account_id == Account.id). \
                    filter(Account.auth_id == auth_id,
                           Account.username == username).all()
            if len(account_phonenum) > 0:
                pipeline = self.redis_client.pipeline()
                pipeline.hset(AuthHandler._REDIS_AUTH_HASH, username, auth_id)
                phonenums = [x.PhoneNumber.number for x in account_phonenum]
                for phonenum in phonenums:
                    pipeline.sadd(username, phonenum)
                pipeline.execute()
                return True, set(phonenums)
            else:
                return False, None
        else:
            if auth_id == cached_auth_id:
                return True, self.redis_client.smembers(username)
            else:
                return False, None

    def check_auth(self, username, auth_id):
        """

        :param str username:
        :param str auth_id:
        :return:
        """
        db_session = self.db_handler.getSession()
        try:
            return self._check_auth(username=username, auth_id=auth_id, db_session=db_session)
        finally:
            db_session.close()
