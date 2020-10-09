from itsdangerous import URLSafeTimedSerializer
from app import trv

def generate_confirmation_token(email):
    """
    This serializes anything including special chars, for this to work, you need to set SECRET_KEY & SECURITY_PASSWORD_SALT.
    Finally, this returns a signed string serialized with the internal serializer (email + SECRET_KEY).
    :param email:
    :return:
    """
    serializer = URLSafeTimedSerializer(trv.config['SECRET_KEY'])                #
    return serializer.dumps(email, salt=trv.config['SECURITY_PASSWORD_SALT'])   #


def confirm_token(token, expiration=None):
    """
    This take the token and verifies it, for this to work you need to provide the SECRET_KEY that was used to generate the token.
    To un-serialize the data, you need to provide SECURITY_PASSWORD_SALT that was used to generate the token.
    :param token:
    :param expiration:
    :return:
    """
    serializer = URLSafeTimedSerializer(trv.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=trv.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
    except:
        return False
    return email
