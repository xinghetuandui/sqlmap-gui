import urllib.parse
import html
import base64
import binascii
import json
import re

class HTTPDecoder:
    @staticmethod
    def url_encode(text: str, plus_space: bool = False) -> str:
        """URL编码
        Args:
            text: 要编码的文本
            plus_space: 是否将空格编码为+号
        """
        try:
            if plus_space:
                return urllib.parse.quote_plus(text)
            return urllib.parse.quote(text)
        except Exception:
            return "编码失败"
        
    @staticmethod
    def url_decode(text: str, plus_space: bool = False) -> str:
        """URL解码"""
        try:
            if plus_space:
                return urllib.parse.unquote_plus(text)
            return urllib.parse.unquote(text)
        except Exception:
            return "解码失败"
            
    @staticmethod
    def html_encode(text: str, quote: bool = True) -> str:
        """HTML编码
        Args:
            text: 要编码的文本
            quote: 是否转换引号
        """
        try:
            return html.escape(text, quote=quote)
        except Exception:
            return "编码失败"
        
    @staticmethod
    def html_decode(text: str) -> str:
        """HTML解码"""
        try:
            return html.unescape(text)
        except Exception:
            return "解码失败"
            
    @staticmethod
    def unicode_encode(text: str, prefix: str = "\\u") -> str:
        """Unicode编码
        Args:
            text: 要编码的文本
            prefix: Unicode前缀，可选 \\u 或 %u
        """
        try:
            return ''.join([f"{prefix}{ord(c):04x}" for c in text])
        except Exception:
            return "编码失败"
        
    @staticmethod
    def unicode_decode(text: str) -> str:
        """Unicode解码"""
        try:
            # 处理 \u 和 %u 两种格式
            text = text.replace('%u', '\\u')
            return text.encode('utf-8').decode('unicode-escape')
        except Exception:
            return "解码失败"
            
    @staticmethod
    def json_encode(text: str, pretty: bool = True) -> str:
        """JSON格式化
        Args:
            text: JSON字符串
            pretty: 是否美化输出
        """
        try:
            data = json.loads(text)
            if pretty:
                return json.dumps(data, indent=2, ensure_ascii=False)
            return json.dumps(data, ensure_ascii=False)
        except Exception:
            return "格式化失败"
            
    @staticmethod
    def jwt_decode(token: str) -> str:
        """JWT解码"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return "无效的JWT格式"
                
            # 解码header和payload
            header = base64.b64decode(parts[0] + '=' * (-len(parts[0]) % 4)).decode()
            payload = base64.b64decode(parts[1] + '=' * (-len(parts[1]) % 4)).decode()
            
            # 格式化输出
            result = "Header:\n"
            result += json.dumps(json.loads(header), indent=2)
            result += "\n\nPayload:\n"
            result += json.dumps(json.loads(payload), indent=2)
            result += f"\n\nSignature:\n{parts[2]}"
            return result
        except Exception:
            return "解码失败" 

def decode_request(request: dict) -> dict:
    """解码HTTP请求数据"""
    result = request.copy()
    
    # 解码URL
    if 'url' in result:
        result['url'] = urllib.parse.unquote(result['url'])
        
    # 解码Headers
    if 'headers' in result:
        headers = []
        for line in result['headers'].split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                decoded_value = urllib.parse.unquote(value.strip())
                decoded_value = html.unescape(decoded_value)
                headers.append(f"{key.strip()}: {decoded_value}")
        result['headers'] = '\n'.join(headers)
        
    # 解码Body
    if 'body' in result:
        body = result['body']
        # URL解码
        body = urllib.parse.unquote(body)
        # HTML解码
        body = html.unescape(body)
        # Base64解码
        try:
            decoded = base64.b64decode(body).decode()
            if all(32 <= ord(c) <= 126 for c in decoded):
                body = decoded
        except:
            pass
        result['body'] = body
        
    return result

def encode_request(request: dict) -> dict:
    """编码HTTP请求数据"""
    result = request.copy()
    
    # 编码URL
    if 'url' in result:
        result['url'] = urllib.parse.quote(result['url'])
        
    # 编码Headers
    if 'headers' in result:
        headers = []
        for line in result['headers'].split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                encoded_value = urllib.parse.quote(value.strip())
                headers.append(f"{key.strip()}: {encoded_value}")
        result['headers'] = '\n'.join(headers)
        
    # 编码Body
    if 'body' in result:
        body = result['body']
        # URL编码
        body = urllib.parse.quote(body)
        result['body'] = body
        
    return result 