import string
import random

def gen_invite_code():
    return ''.join(random.choice(string.digits + string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(64))

if __name__ == '__main__':
    gen_invite_code()

