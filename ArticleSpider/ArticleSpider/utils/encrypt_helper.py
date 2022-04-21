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

if __name__ == '__main__':
    s = '101_3_2.0+/api/v4/answers/542641969/concerned_upvoters?limit=5&offset=0+"ADBejZc60BSPTiQGKCwiS5LGxWQiUtZgyC0=|1650351386"'
    print(g_encrypt(s))
