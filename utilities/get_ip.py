from flask import request

def get_ip():
    ip = ''
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip += request.environ['REMOTE_ADDR']
    else:
        ip += request.environ['HTTP_X_FORWARDED_FOR']
    return ip

