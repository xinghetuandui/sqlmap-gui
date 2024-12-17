import base64

def image_to_base64(image_path: str) -> str:
    """将图片文件转换为Base64编码字符串"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def base64_to_image(base64_str: str) -> bytes:
    """将Base64编码字符串转换回图片数据"""
    return base64.b64decode(base64_str) 