import openai
import configparser
import os

prompt = """
1. 翻译一段英文技术文档为中文，文档中有格式为“PROTECTED$i$”的占位符，其中“i”是数字序号。占位符代表特殊符号或特殊文字，不要翻译占位符，使其保持原本内容。如果文档没有占位符，则直接翻译文档内容。
2. 某些单词可能被占位符包裹，且单词和占位符之间没有空格，务必区分，且翻译后的该单词也要被占位符包裹。
3. 某些单词可能被占位符包裹，且单词和占位符之间有空格，翻译后的该单词也要被占位符包裹且中间有空格。
4. 如果某占位符在待翻译段落的最前面，且该待翻译段落很短且没有句号，则该段落为一个标题，翻译后的该占位符也要在翻译后的段落的最前面。
5. 翻译后保留的占位符要和原始占位符一一对应，比如原始占位符是PROTECTED$11$，翻译后的占位符也要是PROTECTED$11$。
6. 翻译后的文档格式要和原文档保持严格一致。比如，对于文档中出现的换行符，翻译后的内容也要保留换行符。
7. 对于文档中出现的代表专业术语的单词或短语，如果无法翻译，或翻译后不通顺，则保留原始内容，不进行翻译。如果待翻译文本只有特殊符号，则不进行翻译。
8. 在翻译时务必保证语句通顺，符合中文用语习惯。
9. 例子：
    - 输入1：
        If we've enable LangSmith, we can see that this run is PROTECTED$19$ logged PROTECTED$11$ to LangSmith, and can see the PROTECTED$20$.
    - 输出1：
        如果我们启用了 LangSmith，我们可以看到此运行已 PROTECTED$19$ 记录到 PROTECTED$11$ LangSmith，并且可以看到 PROTECTED$20$。
    - 输入2：
        To just simply call the model, we can pass in a list of PROTECTED$11$messagesPROTECTED$12$ to the PROTECTED$13$.invokePROTECTED$14$ method.
    - 输出2：
        为了简单地调用模型，我们可以将一系列 PROTECTED$11$消息PROTECTED$12$ 传递给 PROTECTED$13$.invokePROTECTED$14$ 方法。
    - 输入3：
        PROTECTED$11$ Chaining together components with LCEL
    - 输出3：
        PROTECTED$11$ 将组件与 LCEL 连接在一起
    - 输入4：
        :::
    - 输出4：
        :::
10. 下面我将发送待翻译文本，请直接输出翻译后的内容，不要输出任何其他内容，直接返回翻译后的文本，不要使用任何其他前缀或后缀，不要使用任何其他标记，比如```等。
请翻译以下内容：

"""


# 读取配置文件
config = configparser.ConfigParser()
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'config.ini')
config.read(config_path)

# 从配置文件中获取 API 密钥
api_key = config.get('OpenAI', 'api_key')
base_url = config.get('OpenAI', 'base_url')
model_name = config.get('OpenAI', 'model_name')

# 设置 OpenAI 的 API Key 和 API 基础地址
openai.api_key = api_key
openai.base_url = base_url
openai.default_headers = {"x-foo": "true"}


def ai_translate(markdown_text, model_name=model_name, max_retries=2, multiply=2):
    for attempt in range(max_retries):
        completion = openai.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt + markdown_text,
                },
            ]
        )
        translated_text = completion.choices[0].message.content
        
        # 检查翻译后的文本长度是否超过原文的 multiply 倍
        if len(translated_text) <= len(markdown_text) * multiply:
            return translated_text
        
        # 如果长度超过 multiply 倍,且不是最后一次尝试,则继续重试
        if attempt < max_retries - 1:
            print(f"翻译结果过长,正在进行第{attempt+2}次尝试...")
    
    # 如果所有尝试都失败,返回最后一次的翻译结果
    return translated_text

if __name__ == "__main__":
    markdown_text = """
Notice that the response from the model is an PROTECTED${2}$AIMessagePROTECTED${3}$. This contains a string response along with other metadata about the response. Oftentimes we may just want to work with the string response. We can parse out just this response by using a simple output parser."""

    print(ai_translate(markdown_text))
