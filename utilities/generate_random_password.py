import string
import random

def gen_password():
    return ''.join(random.choice(string.digits + string.ascii_uppercase + string.ascii_lowercase + string.punctuation) for _ in range(16)) + '@6aX'

if __name__ == '__main__':
    gen_password()

