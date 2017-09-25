import json


class APIException(Exception):
    def __init__(self, message, http_status):
        """
        :param str message: Error message sent back to client.
        :param int http_status: The http status to return for this exception.
        """
        self.message = message
        self.http_status = http_status


def check_arg_len(arg_value, min_len, max_len):
    """

    :param str arg_value:
    :param int min_len:
    :param int max_len:
    :return:
    """
    arg_len = len(arg_value)
    if arg_len < min_len or arg_len > max_len:
        return False
    return True


def check_arg_validity(arg_name, arg_value):
    """

    :param str arg_name:
    :param str arg_value:
    :return:
    """
    if arg_name == 'from':
        return check_arg_len(arg_value=arg_value, min_len=6, max_len=16)
    elif arg_name == 'to':
        return check_arg_len(arg_value=arg_value, min_len=6, max_len=16)
    elif arg_name == 'text':
        return check_arg_len(arg_value=arg_value, min_len=1, max_len=120)


def check_arg_sanity(arg_name, arg_value):
    """

    :param str arg_name:
    :param str arg_value:
    :return:
    """
    response = {"message": "", "error": ""}
    if arg_value is None:
        response["error"] = "%s is missing" % arg_name
        raise APIException(message=json.dumps(response), http_status=400)
    if not check_arg_validity(arg_name=arg_name, arg_value=arg_value):
        response["error"] = "%s is invalid" % arg_name
        raise APIException(message=json.dumps(response), http_status=400)


def arg_validate(from_number, to_number, text):
    """

    :param str from_number:
    :param str to_number:
    :param str text:
    :return:
    """
    check_arg_sanity(arg_name='from', arg_value=from_number)
    check_arg_sanity(arg_name='to', arg_value=to_number)
    check_arg_sanity(arg_name='text', arg_value=text)


def payload_validate(payload):
    """

    :param str payload:
    :return:
    """
    try:
        payload = json.loads(payload)
    except ValueError:
        raise APIException(message=json.dumps({"message": "", "error": "invalid payload"}),
                           http_status=400)
    from_number = payload.get('from')
    to_number = payload.get('to')
    text = payload.get('text')
    arg_validate(from_number=from_number, to_number=to_number, text=text)
    return from_number, to_number, text
