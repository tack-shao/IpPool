# -*- coding: utf-8 -*-
# @时间      :2019/3/25 上午7:59
# @作者      :tack
# @网站      :
# @文件      :PRPCrypt.py
# @说明      :

import base64
import datetime
import hashlib
import random

from Crypto.Cipher import AES
from hashlib import md5, sha1
from binascii import b2a_hex, a2b_hex


# two functions to pad(when do encryption) and unpad(when do decryption) when the length of input is not a multiple
# of BLOCK_SIZE
BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]


class PRPCrypt:
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC

    # 加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip(b'\0')

    # 解密，去掉补足的空格用 strip() 去掉
    def decrypt4gbk(self, text):
        sha384 = hashlib.sha384()
        sha384.update(self.key.encode('utf-8'))
        # res = sha384.digest().encode('hex')
        res = sha384.digest()
        key = res[0:32]
        iv = res[32:48]
        cryptor = AES.new(key, self.mode, iv)
        plain_text = cryptor.decrypt(base64.encodebytes(text))
        return plain_text.rstrip('\0')

    def get_enc_key(self):
        sha384 = hashlib.sha384()
        sha384.update(self.key.encode('utf-8'))
        res = sha384.digest()
        return res
