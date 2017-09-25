import json
import unittest

import api_payload_validator
from api_payload_validator import APIException


class TestApiPayloadValidator(unittest.TestCase):

    def test_check_arg_len(self):
        self.assertTrue(api_payload_validator.check_arg_len('9740171794', 6, 16))
        self.assertFalse(api_payload_validator.check_arg_len('97401717949740171794', 6, 16))
        self.assertFalse(api_payload_validator.check_arg_len('97401', 6, 16))

    def test_check_arg_validity(self):
        self.assertTrue(api_payload_validator.check_arg_validity('from', '9740171794'))
        self.assertTrue(api_payload_validator.check_arg_validity('to', '9740171794'))
        self.assertTrue(api_payload_validator.check_arg_validity('text', 'STOP'))

    def test_check_arg_sanity(self):
        try:
            api_payload_validator.check_arg_sanity('from', None)
        except APIException as ae:
            self.assertEquals(ae.http_status, 400)
            self.assertEquals(ae.message, json.dumps({"message": "", "error": "from is missing"}))
        try:
            api_payload_validator.check_arg_sanity('from', '97401717949740171794')
        except APIException as ae:
            self.assertEquals(ae.http_status, 400)
            self.assertEquals(ae.message, json.dumps({"message": "", "error": "from is invalid"}))

    def test_arg_validate(self):
        api_payload_validator.arg_validate('9740171794', '9740171795', 'STOP')
        self.assertRaises(APIException, api_payload_validator.arg_validate, '97401717949740171794', '9740171794', 'STOP')
        self.assertRaises(APIException, api_payload_validator.arg_validate, '9740171794', '97401717949740171794', 'STOP')
        self.assertRaises(APIException, api_payload_validator.arg_validate, '9740171794', '9740171794', '')

    def test_payload_validate(self):
        payload_json = {
            'from': '9740171794',
            'to': '9740171795',
            'text': 'STOP',
        }
        payload = json.dumps(payload_json)
        from_number, to_number, text = api_payload_validator.payload_validate(payload)
        self.assertEquals('9740171794', from_number)
        self.assertEquals('9740171795', to_number)
        self.assertEquals('STOP', text)
        try:
            api_payload_validator.payload_validate(payload[:-1])
        except APIException as ae:
            self.assertEquals(ae.http_status, 400)
            self.assertEquals(ae.message, json.dumps({"message": "", "error": "invalid payload"}))


