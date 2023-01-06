import json
from hashlib import md5
from typing import Union

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


class Message4Pairing:
    """
    Packet Structure:
        <BytesPackage>:
            |<-----------32bit----------->|<---------rest--------->|
                 md5(<BinaryContents>)         <BinaryContents>

        <BinaryContents>:
            ("anonymPairing" + <Contents>).encode('UTF-8')

        <Contents>:
            if key==None:
                json(PythonDict)
            if not key== None:
                PKCS1_OAEP.encrypt(RsaKey, json(PythonDict))
    """

    __prefix = 'anonymPairing'

    def __init__(self, data: Union[dict, bytes], key: Union[None, RSA.RsaKey] = None):
        self.__key = key

        if isinstance(data, bytes):
            self.__encryptable = False
            self.__content = self.__unpacker(data)
        elif isinstance(data, dict):
            self.__encryptable = True
            self.__content = data
        else:
            raise ValueError("Can not parse data")

    @property
    def encryptable(self) -> bool:
        """Whether this instance can be encrypted"""
        return self.__encryptable

    @property
    def decryptable(self) -> bool:
        """Whether this instance can be decrypted"""
        return not self.__encryptable

    def to_dict(self) -> dict:
        """Creates a dict from a Message4Pairing"""
        return self.__content

    def to_bytes(self) -> bytes:
        """Creates a bytes from a Message4Pairing"""
        return self.__packager(self.__content)

    def __packager(self, content: dict) -> bytes:
        """Packager"""
        if not self.encryptable:
            raise TimeoutError('This instance cannot be encoded')

        plain_text = json.dumps(content)
        plain_text = self.__prefix + plain_text

        bin_text = plain_text.encode('UTF-8')

        if self.__key is not None:
            cipher = PKCS1_OAEP.new(self.__key)
            bin_text = cipher.encrypt(bin_text)

        return md5(bin_text).hexdigest().encode('UTF-8') + bin_text

    def __unpacker(self, pack: bytes) -> dict:
        """Unpacker"""
        if not self.decryptable:
            raise TimeoutError('This instance cannot be decoded')

        # noinspection PyBroadException
        try:
            bin_text = pack[32:]

            if not pack[:32].decode() == md5(bin_text).hexdigest():
                return {}

            if self.__key is not None:
                cipher = PKCS1_OAEP.new(self.__key)
                bin_text = cipher.decrypt(bin_text)

            plain_text = bin_text.decode('UTF-8')

            if plain_text[:len(self.__prefix)] == self.__prefix:
                return json.loads(plain_text[len(self.__prefix):])
        except Exception:
            return {}
