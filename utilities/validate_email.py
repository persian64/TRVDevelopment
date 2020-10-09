import re

def validate_email(email):
    """
    Validates a given email address, returns True if an Email is valid and False otherwise.
    :param email:
    :return:
    """
    return bool(re.match(r"(^[a-zA-Z0-9_.+-]+@(gmail|yahoo|protonmail|outlook|zoho|aim|aol|icloud|yandex)+\.[a-zA-Z0-9]|\.[a-zA-Z0-9]+$)", str(email)))

if __name__ == '__main__':
    validate_email(email='jack@me.com')
