import json
from functools import wraps

import api_payload_validator
import redis
from apirate_limiter import APIRateLimiter, RateLimitExceededException
from auth_handler import AuthHandler
from blacklist_manager import BlacklistManager
from db_handler import PostgresDBHandler
from flask import Flask, request, Response, g

app = Flask(__name__)
_response_type = 'application/json'
app_state = {}


@app.errorhandler(api_payload_validator.APIException)
def error_handler(api_exception):
    """

    :param APIException api_exception:
    :return:
    """
    response = Response(response=api_exception.message,
                        status=api_exception.http_status,
                        mimetype=_response_type)
    return response


def check_auth(username, auth_id):
    """
    :param str username:
    :param str auth_id:
    :return:
    """
    auth_handler = app_state['auth_handler']
    auth_valid, phonenums = auth_handler.check_auth(username=username, auth_id=auth_id)
    if not auth_valid:
        return False
    g.phonenums = phonenums
    return True


def authenticate_error():
    """
    sends HTTP 403 message
    :return:
    """
    return Response(response=json.dumps('Invalid credentials, please provide correct username and password'),
                    status=403, mimetype=_response_type)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(username=auth.username, auth_id=auth.password):
            return authenticate_error()
        return f(*args, **kwargs)
    return decorated


@app.route("/inbound/sms", methods=['POST'])
@requires_auth
def inbound():
    payload = request.data
    from_number, to_number, text = api_payload_validator.payload_validate(payload=payload)
    this_account_phonenums = g.phonenums
    if to_number not in this_account_phonenums:
        raise \
            api_payload_validator.APIException(message=json.dumps({"message": "", "error": "to parameter not found"}),
                                               http_status=400)
    if text in ['STOP', 'STOP\r', 'STOP\r\n']:
        blacklist_manager = app_state['blacklist_manager']
        blacklist_manager.blacklist(from_number=from_number, to_number=to_number)
    return Response(response=json.dumps({"message": "inbound sms ok", "error": ""}), status=200,
                    mimetype=_response_type)


@app.route("/outbound/sms", methods=['POST'])
@requires_auth
def outbound():
    payload = request.data
    from_number, to_number, text = api_payload_validator.payload_validate(payload=payload)
    this_account_phonenums = g.phonenums
    if from_number not in this_account_phonenums:
        raise api_payload_validator.APIException(message=json.dumps({"message": "", "error": "from parameter not found"}),
                                                 http_status=400)
    blacklist_manager = app_state['blacklist_manager']
    if blacklist_manager.check_blacklist(from_number=from_number, to_number=to_number):
        return Response(response=json.dumps({"message": "",
                                             "error": "sms from %s to %s blocked by STOP request" %
                                                      (from_number, to_number)}),
                        status=200, mimetype=_response_type)
    apirate_limiter = app_state['apirate_limiter']
    try:
        apirate_limiter.ratelimit(from_number=from_number)
    except RateLimitExceededException as rle:
        return Response(response=json.dumps({"message": "", "error": rle.message}), status=429,
                        mimetype=_response_type)
    return Response(response=json.dumps({"message": "outbound sms ok", "error": ""}), status=200,
                    mimetype=_response_type)


def init_app():
    """Initialize stuff that the server app needs.
    :param args: dictionary of commandline arguments.
    """

    db_config = {
        'user': 'postgres',
        'host': 'localhost',
        'database': 'postgres'
    }
    db_handler = PostgresDBHandler(config=db_config)
    redis_client = redis.Redis(host='127.0.0.1')
    app_state['blacklist_manager'] = BlacklistManager(redis_client=redis_client)
    app_state['apirate_limiter'] = APIRateLimiter(redis_client=redis_client)
    app_state['auth_handler'] = AuthHandler(redis_client=redis_client, db_handler=db_handler)


if __name__ == "__main__":
    # initialise the app
    init_app()
    app.run(host='0.0.0.0', threaded=True)
