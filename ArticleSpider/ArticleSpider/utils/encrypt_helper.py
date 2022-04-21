import os
import hashlib
import execjs

BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

def md5(str):
    return hashlib.md5(str.encode(encoding='utf-8')).hexdigest()

def g_encrypt(str):
    with open(BASE_DIR + '/utils/g_encrypt.js', 'r') as f:
        encryption = execjs.compile(f.read())
        # call b encryption function with param str
        return encryption.call("b", str)
