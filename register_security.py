import base64
import hashlib
import time
import re

from schema import models
from Cryptodome import Random
from Cryptodome.Cipher import AES
from datetime import datetime

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


class AccountValidator:
    def __init__(self, data, check_list = ['all']):
        self.result = True
        self.check_list = ['id', 'nickname', 'password', 'password_c']
        self.isDupchecked = False
        
        if (check_list[0] != 'all'):
            self.check_list = check_list

        if set(data.keys()).difference(self.check_list) != set():
            raise KeyError

        self.id = data.get('id', '')
        self.nickname = data.get('nickname', '')
        self.password = data.get('password', '')
        self.confrim_password = data.get('password_c', '')

    
    def check_regexps(self, type):
        regexps = ['[^a-zA-Z0-9]', '\s', '[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]', '[0-9]', '[a-zA-Z]', '[`~!@@#$%^&*|₩₩₩\'₩\";:₩/?]']
        pos = 0
        if (type == 'id'):
            for exp in regexps[:2]:
                p = re.compile(exp)
                pos = p.search(self.id)
                if pos is not None:
                    break
        elif (type == 'nickname'):
            p = re.compile(regexps[1])
            pos = p.search(self.nickname)
        elif (type == 'password'):
            for exp in regexps[1:3]:
                p = re.compile(exp)
                pos = p.search(self.id)
                if pos is not None:
                    break
            
            num = re.search(regexps[3], self.password)
            eng = re.search(regexps[4], self.password)
            spe = re.search(regexps[5], self.password)
            if (None in [num, eng, spe]):
                pos = 0
        else:
            return pos
        
        return pos

    def is_duplicated(self):
        self.isDupchecked = True
        user = models.User(None, None, None)
        lower_id = user.query.filter_by(user_id = self.id.lower()).first()
        upper_id = user.query.filter_by(user_id = self.id.upper()).first()

        if (lower_id is not None or upper_id is not None):
            return True
        else:
            return False

    def validate_id(self):
        MIN_LENGTH = 4
        MAX_LENGTH = 16
        
        if (not self.isDupchecked and self.is_duplicated()):
            self.result = False
        
        if (len(self.check_list) == 1): # if only duplicate check
            return

        if (self.check_regexps('id') is not None):
            self.result = False
        elif (len(self.id) < MIN_LENGTH or len(self.id) > MAX_LENGTH):
            self.result = False

    def validate_nickname(self):
        MIN_LENGTH = 2
        MAX_LENGTH = 16
        
        if (self.check_regexps('nickname') is not None):
            self.result = False
        elif (len(self.nickname) < MIN_LENGTH or len(self.nickname) > MAX_LENGTH):
            self.result = False

    def validate_password(self):
        MIN_LENGTH = 8
        MAX_LENGTH = 32
        
        if (self.check_regexps('password') is not None):
            self.result = False
        elif (len(self.password) < MIN_LENGTH or len(self.password) > MAX_LENGTH):
            self.result = False
        elif (self.confrim_password and self.password != self.confrim_password):
            self.result = False
    
    def validate(self):
        if 'id' in self.check_list:
            self.validate_id()
        if 'nickname' in self.check_list:
            self.validate_nickname()
        if 'password' in self.check_list:
            self.validate_password()


if __name__ == "__main__":
    data = {'id' : 'aaaaa1'}
    validator = AccountValidator(data, ['id'])
    validator.validate()
    print(validator.result)
