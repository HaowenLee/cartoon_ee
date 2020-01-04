import base64
from urllib import parse

from Crypto.Cipher import AES
import requests
from contextlib import closing
import src.keys as keys
import json

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)"
}


# 解密后，去掉补足的空格用strip()去掉
def decrypt(text):
    # url解码
    url_encode = parse.unquote(text)
    # base64解码
    base64_encode = base64.decodebytes(bytes(url_encode, 'utf-8'))
    # AES加密
    cryptor = AES.new(keys.TEXT_KEY.encode('utf-8'), AES.MODE_ECB)
    plain_text = cryptor.decrypt(base64_encode)
    return bytes.decode(plain_text).rstrip('\0')


# 解密 bytes -> bytes
def bytes_decrypt(text):
    # AES加密
    cryptor = AES.new(keys.IMAGE_KEY.encode('utf-8'), AES.MODE_ECB)
    plain_text = cryptor.decrypt(text)
    return plain_text


# 文件下载器
def download_image(file_url, file_path):
    with closing(requests.get(file_url, headers=headers, stream=True)) as response:
        chunk_size = 1024  # 单次请求最大值
        content_size = int(response.headers['content-length'])  # 内容体总大小
        data_count = 0
        with open(file_path, "wb") as file:
            for data in response.iter_content(chunk_size=chunk_size):
                # 解密数据
                data = bytes_decrypt(data)
                file.write(data)
                data_count = data_count + len(data)
                now_jd = (data_count / content_size) * 100
                print("\r 文件下载进度：%d%%(%d/%d) - %s" % (now_jd, data_count, content_size, file_path), end=" ")


# 批量下载
def batch_download_image(response):
    bean = json.loads(response)
    print(bean['result'])
    result_json = decrypt(bean['result'])
    print(result_json)
    data = json.loads(result_json)
    index = 0
    for item in data['data']:
        download_image(item['image_url'], "../out/" + str(index) + ".jpg")
        index += 1
