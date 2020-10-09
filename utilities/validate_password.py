import re
import random
import string

def validate_password(password):
    """
    Returns True if the password is strong and False otherwise
    :param password:
    :return:
    """
    return bool(re.match('((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{10,64})', str(password)))

if __name__ == '__main__':
    validate_password('Correc7@')





