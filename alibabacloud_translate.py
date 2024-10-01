from alibabacloud_alimt20181012.client import Client as alimt20181012Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alimt20181012 import models as alimt_20181012_models
from alibabacloud_tea_util import models as util_models

from text import correct_markdown_syntax, occupy_text, markdown_text2

import configparser
import os

# 读取配置文件
config = configparser.ConfigParser()
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'config.ini')
config.read(config_path)

# 从配置文件中获取 API 密钥
access_key_id = config.get('AlibabaCloud', 'access_key_id')
access_key_secret = config.get('AlibabaCloud', 'access_key_secret')
 
def create_client(
    access_key_id: str,
    access_key_secret: str,
) -> alimt20181012Client:
    config = open_api_models.Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret
    )
    config.endpoint = f'mt.cn-hangzhou.aliyuncs.com'
    return alimt20181012Client(config)


def ali_translate(text):
    client = create_client(access_key_id, access_key_secret)
    translate_general_request = alimt_20181012_models.TranslateGeneralRequest(
        format_type='text',
        source_language='en',
        target_language='zh',
        source_text=text,
        scene='general'
    )
    runtime = util_models.RuntimeOptions()
    resp = client.translate_general_with_options(translate_general_request, runtime)
    return resp.body.data.__dict__['translated']

if __name__ == "__main__":
    # 使用 <ALIMT > 和 </ALIMT> 包裹的文本不会被翻译
    # print(translate("For further reading on the core concepts of LangChain, we've got detailed <ALIMT > PROTECTED_0 </ALIMT>"))
    
    text, placeholder_dict = occupy_text(markdown_text2)
    print(text)
    print(ali_translate(text))