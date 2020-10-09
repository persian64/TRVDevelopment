import re

def validate_username(username):
    """
    Validates a username, returns True if the username is valid and False otherwise.
    :param username:
    :return:
    """
    return bool(re.fullmatch(r"[a-zA-Z0-9_.]{6,16}", str(username)))

if __name__ == '__main__':
    validate_username(username='jack')

