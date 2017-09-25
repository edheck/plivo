import unittest

from auth_handler import AuthHandler
from db_handler import PostgresDBHandler
from mock.mock import MagicMock
from models import Account, PhoneNumber
from sqlalchemy.orm.session import Session


class TestAuthHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db_config = {
            'user': 'postgres',
            'host': 'localhost',
            'database': 'postgres'
        }
        cls.db_handler = PostgresDBHandler(config=db_config)

    def setUp(self):
        redis_client = MagicMock()
        self.auth_handler = AuthHandler(redis_client=redis_client, db_handler=self.db_handler)

    def test_check_auth_redis_miss(self):
        db_handler = self.auth_handler.db_handler
        db_conn = db_handler.getEngine().connect()
        db_txn = db_conn.begin()
        try:
            db_session = Session(bind=db_conn)
            try:
                account = Account(auth_id='some_auth_id', username='some_user')
                db_session.add(account)
                db_session.flush()
                phonenumber = PhoneNumber(number='9740171794', account_id=account.id)
                db_session.add(phonenumber)
                db_session.commit()
                self.auth_handler.redis_client.hget.return_value = None
                self.auth_handler.redis_client.pipeline.return_value = redis_pipeline_mock = MagicMock()
                status, phonenums = self.auth_handler._check_auth('some_user', 'some_auth_id', db_session)
                self.assertTrue(status)
                self.assertEquals(set(['9740171794']), phonenums)
                self.assertEquals(redis_pipeline_mock.hset.call_count, 1)
                redis_pipeline_mock.hset.assert_called_with(self.auth_handler._REDIS_AUTH_HASH, 'some_user', 'some_auth_id')
                self.assertEquals(redis_pipeline_mock.sadd.call_count, 1)
                redis_pipeline_mock.sadd.assert_called_with('some_user', '9740171794')
                self.assertEquals(redis_pipeline_mock.execute.call_count, 1)
            finally:
                db_session.close()
        finally:
            db_txn.rollback()
            db_conn.close()

    def test_check_auth_redis_miss_wrong_auth_id(self):
        db_handler = self.auth_handler.db_handler
        db_conn = db_handler.getEngine().connect()
        db_txn = db_conn.begin()
        try:
            db_session = Session(bind=db_conn)
            try:
                account = Account(auth_id='some_auth_id', username='some_user')
                db_session.add(account)
                db_session.flush()
                phonenumber = PhoneNumber(number='9740171794', account_id=account.id)
                db_session.add(phonenumber)
                db_session.commit()
                self.auth_handler.redis_client.hget.return_value = None
                status, phonenums = self.auth_handler._check_auth('some_user', 'faulty_auth_id', db_session)
                self.assertFalse(status)
                self.assertEquals(None, phonenums)
            finally:
                db_session.close()
        finally:
            db_txn.rollback()
            db_conn.close()

    def test_check_auth_redis_hit(self):
        self.auth_handler.redis_client.hget.return_value = 'some_auth_id'
        self.auth_handler.redis_client.smembers.return_value = set(['9740171794'])
        status, phonenums = self.auth_handler._check_auth('some_user', 'some_auth_id', None)
        self.assertTrue(status)
        self.assertEquals(set(['9740171794']), phonenums)

    def test_check_auth_redis_hit_wrong_auth_id(self):
        self.auth_handler.redis_client.hget.return_value = 'some_auth_id'
        self.auth_handler.redis_client.smembers.return_value = set(['9740171794'])
        status, phonenums = self.auth_handler._check_auth('some_user', 'faulty_auth_id', None)
        self.assertFalse(status)
        self.assertEquals(None, phonenums)




