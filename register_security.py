import base64
import hashlib
import time
import re

from Cryptodome import Random
from Cryptodome.Cipher import AES
from datetime import datetime, timedelta

REGISTER_SECRET_KEY = "REGISTER_SECRET_KEY"
MAINTAIN_TIME_MIN = 3 * 60.0;

class RegisterCipher:
    def __init__(self):
        self.BS = 16
        self.pad = lambda s: s + (self.BS - len(s) % self.BS) * chr(self.BS -len(s) % self.BS)
        self.unpad = lambda s: s[0:-s[-1]]
        self.key = hashlib.sha256(REGISTER_SECRET_KEY.encode('utf-8')).digest()
        self.genTime = str(datetime.now())
    
    def encrypt(self, raw):
        raw = self.pad(raw).encode('utf-8')
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.urlsafe_b64encode(iv + cipher.encrypt( raw ))

    def decrypt(self, enc):
        enc = base64.urlsafe_b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(enc[16:]))
    
    def encrypt_str(self, raw):
        return self.encrypt(raw).decode('utf-8')
    
    def decrypt_str(self, enc):
        if type(enc) == str:
            enc = str.encode(enc)
        return self.decrypt(enc).decode('utf-8')
    
    def get_timeover(self, now):
        return (datetime.strptime(self.genTime, '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(now, '%Y-%m-%d %H:%M:%S.%f')).seconds >= MAINTAIN_TIME_MIN

if __name__ == "__main__":
    rg = RegisterCipher()
    enc = rg.encrypt_str(rg.genTime)
    # raw = rg.decrypt_str("uH6saN3sKTeEO7fG4MU5gliBlo3EEbC5C0+AyOghAwAJYnlgzjHo6ij5fNXw623C")
    print(enc)
    # print(raw)
