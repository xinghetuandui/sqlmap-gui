import base64
import binascii
import zlib
import hashlib
from typing import Union

class BinaryDecoder:
    @staticmethod
    def base64_encode(text: str) -> str:
        """Base64编码"""
        try:
            return base64.b64encode(text.encode()).decode()
        except Exception:
            return "编码失败"
            
    @staticmethod
    def base64_decode(text: str) -> str:
        """Base64解码"""
        try:
            # 自动处理填充
            padding = 4 - (len(text) % 4)
            if padding != 4:
                text += '=' * padding
            return base64.b64decode(text.encode()).decode()
        except Exception:
            return "解码失败"
            
    @staticmethod
    def hex_encode(text: str) -> str:
        """十六进制编码"""
        try:
            return binascii.hexlify(text.encode()).decode()
        except Exception:
            return "编码失败"
            
    @staticmethod
    def hex_decode(text: str) -> str:
        """十六进制解码"""
        try:
            # 移除空格、换行符和0x前缀
            text = ''.join(text.replace('0x', '').split())
            return binascii.unhexlify(text.encode()).decode()
        except Exception:
            return "解码失败"
            
    @staticmethod
    def hash_encode(text: str, algorithm: str = 'md5') -> str:
        """计算哈希值
        Args:
            text: 要计算哈希的文本
            algorithm: 哈希算法(md5/sha1/sha256/sha512)
        """
        try:
            if algorithm == 'md5':
                return hashlib.md5(text.encode()).hexdigest()
            elif algorithm == 'sha1':
                return hashlib.sha1(text.encode()).hexdigest()
            elif algorithm == 'sha256':
                return hashlib.sha256(text.encode()).hexdigest()
            elif algorithm == 'sha512':
                return hashlib.sha512(text.encode()).hexdigest()
            else:
                return "不支持的哈希算法"
        except Exception:
            return "计算失败"
            
    @staticmethod
    def gzip_encode(text: str) -> str:
        """Gzip压缩并Base64编码"""
        try:
            compressed = zlib.compress(text.encode())
            return base64.b64encode(compressed).decode()
        except Exception:
            return "压缩失败"
            
    @staticmethod
    def gzip_decode(text: str) -> str:
        """Base64解码并Gzip解压"""
        try:
            compressed = base64.b64decode(text)
            return zlib.decompress(compressed).decode()
        except Exception:
            return "解压失败" 