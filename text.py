import re

markdown_text = """
# Title 1

## Title 2

### Title 3

Here is some inline `code` some `text` here.

Title 1
===============

Title 2
--------

### Title 3

![这是图片](/assets/img/philly-magic-garden.jpg "Magic Gardens")

```
#!/usr/bin/env python
from typing import List

from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langserve import add_routes
```
and 
```python
print("Hello, World!")
```

And here is a [link](https://example.com).

I just love **bold text**.
I just love __bold text__.
Love**is**bold.

Italicized text is the *cat's meow*.
df_dg is a word.
Italicized text is the _cat's meow_.
A*cat*meow

> Dorothy followed her through many of the beautiful rooms in her castle.
>
> The Witch bade her clean the pots and kettles and sweep the floor and keep the fire fed with wood.

1. First item
2. Second item
3. Third item
4. Fourth item

- First item
- Second it-em
- Third item
- Fourth item

This **word** is bold. This <em>word</em> is italic.

- [LangSmith](https://docs.smith.langchain.com)
"""

markdown_text2 = """
## OutputParsers

Notice that the response from the model is an `AIMessage`. This `contains` a string response along with other metadata about the response. Oftentimes we may just want to work with the string response. We can parse out just this response by using a simple output parser.

We first import the simple output parser.
"""

def replace_with_placeholder(match, placeholder_dict, placeholder_counter, is_contain_html_label=True):
    if is_contain_html_label:
        placeholder = f'<ALIMT > PROTECTED${placeholder_counter[0]}$ </ALIMT>'
    else:
        placeholder = f'PROTECTED${placeholder_counter[0]}$'
    placeholder_dict[f'PROTECTED${placeholder_counter[0]}$'] = match.group()
    placeholder_counter[0] += 1
    return placeholder

def occupy_text(text, is_contain_html_label=True):
    """
    将markdown块内容中不翻译的部分使用占位符占位，并使用 <ALIMT > 和 </ALIMT> 包裹占位符
    1. 匹配代码块，（``` 和 ``` 之间）
    2. 匹配行内代码，（` 和 ` 之间）
    3. 匹配图片，（![alt text](image_url)）
    4. 匹配链接，（[link](https://example.com)）
    5.1. 匹配标题符号，（#、##、###、####、#####、###### 等）
    5.2. 匹配标题符号，（任意数量的 == 号来标识一级标题，或者 -- 号来标识二级标题）
    6.1. 匹配加粗符号，（成对出现的 ** 符号）
    6.2. 匹配加粗符号，（成对出现的 __ 符号）
    7.1. 匹配斜体符号，（成对出现的 * 符号）
    7.2. 匹配斜体符号，（成对出现的 _ 符号）
    8. 匹配引用符号，（> 符号）
    9. 匹配无序列表，（- 或 * 符号）
    10. 匹配有序列表，（数字 + . 符号）
    """
    placeholder_dict = {}
    placeholder_counter = [11]  # 使用列表来存储计数器，以便可以在函数内部修改

    # 1. 匹配代码块,(``` 和 ``` 之间)
    code_block_pattern = re.compile(r'```[\s\S]*?```', re.DOTALL)
    text = code_block_pattern.sub(lambda match: replace_with_placeholder(match, placeholder_dict, placeholder_counter, is_contain_html_label), text)

    # 2. 匹配行内代码，（` 和 ` 之间）
    inline_code_pattern = re.compile(r'`[^`\n]+`')
    text = inline_code_pattern.sub(lambda match: replace_with_placeholder(match, placeholder_dict, placeholder_counter, is_contain_html_label), text)

    # 3. 匹配图片，（![alt text](image_url)）
    image_pattern = re.compile(r'!\[[^\]]*\]\([^\)]*\)')
    text = image_pattern.sub(lambda match: replace_with_placeholder(match, placeholder_dict, placeholder_counter, is_contain_html_label), text)

    # 4. 匹配链接，（[link](https://example.com)）
    link_pattern = re.compile(r'\[[^\]]*\]\([^\)]*\)')
    text = link_pattern.sub(lambda match: replace_with_placeholder(match, placeholder_dict, placeholder_counter, is_contain_html_label), text)

    # 5.1. 匹配标题符号，（#、##、###、####、#####、###### 等）
    header_pattern = re.compile(r'^(#{1,6})', re.MULTILINE)
    text = header_pattern.sub(lambda match: replace_with_placeholder(match, placeholder_dict, placeholder_counter, is_contain_html_label), text)
    
    # 5.2. 匹配标题符号，（任意数量的 == 号或 -- 号来标识标题）
    underline_header_pattern = re.compile(r'^([=]{2,}|[-]{2,})$', re.MULTILINE)
    text = underline_header_pattern.sub(lambda match: replace_with_placeholder(match, placeholder_dict, placeholder_counter, is_contain_html_label), text)

    # 6.1. 匹配加粗符号，（成对出现的 ** 符号）
    bold_pattern1 = re.compile(r'\*\*')
    text = bold_pattern1.sub(lambda match: replace_with_placeholder(match, placeholder_dict, placeholder_counter, is_contain_html_label), text)

    # 6.2. 匹配加粗符号，（成对出现的 __ 符号）  
    bold_pattern2 = re.compile(r'__')
    text = bold_pattern2.sub(lambda match: replace_with_placeholder(match, placeholder_dict, placeholder_counter, is_contain_html_label), text)

    # 7.1. 匹配斜体符号，（成对出现的 * 符号）
    italic_pattern1 = re.compile(r'\*')  
    text = italic_pattern1.sub(lambda match: replace_with_placeholder(match, placeholder_dict, placeholder_counter, is_contain_html_label), text)

    # 7.2. 匹配斜体符号，（成对出现的 _ 符号）
    italic_pattern2 = re.compile(r'_')
    text = italic_pattern2.sub(lambda match: replace_with_placeholder(match, placeholder_dict, placeholder_counter, is_contain_html_label), text)

    # 8. 匹配引用符号,（> 符号）
    quote_pattern = re.compile(r'(?m)^>(?=\s)')
    text = quote_pattern.sub(lambda match: replace_with_placeholder(match, placeholder_dict, placeholder_counter, is_contain_html_label), text)

    # 9. 匹配无序列表,（- 或 * 符号）
    unordered_list_pattern = re.compile(r'(?m)^[-*](?=\s)')
    text = unordered_list_pattern.sub(lambda match: replace_with_placeholder(match, placeholder_dict, placeholder_counter, is_contain_html_label), text)

    # 10. 匹配有序列表,（数字 + . 符号）
    ordered_list_pattern = re.compile(r'(?m)^\d+\.(?=\s)')
    text = ordered_list_pattern.sub(lambda match: replace_with_placeholder(match, placeholder_dict, placeholder_counter, is_contain_html_label), text)

    return text, placeholder_dict


def correct_markdown_syntax(text):
    # 修正标题语法（移除前导空格）
    text = re.sub(r'^(\s+)(#{1,6}\s+)', r'\2', text, flags=re.MULTILINE)

    # 修正加粗语法
    text = re.sub(r'(?<!\*)\*\*\s+([^\s*](?:.*?[^\s*])?)\s+\*\*(?!\*)', r'**\1**', text)
    text = re.sub(r'(?<!_)__\s+([^\s_](?:.*?[^\s_])?)\s+__(?!_)', r'__\1__', text)
    
    # 修正斜体语法
    text = re.sub(r'(?<!\*)\*\s+([^\s*](?:.*?[^\s*])?)\s+\*(?!\*)', r'*\1*', text)
    text = re.sub(r'(?<!_)_\s+([^\s_](?:.*?[^\s_])?)\s+_(?!_)', r'_\1_', text)

     # 修正列表格式（删除 "-" 前后的额外空格，以及行尾的空格）
    text = re.sub(r'^\s*-\s+(.*?)\s*$', r'- \1', text, flags=re.MULTILINE)
    
    return text


def is_fully_protected(text, translate_engine):
    """
    检查文本是否完全由占位符组成
    """
    # 使用正则表达式去除所有空白字符（包括空格、制表符、换行符等）
    text = re.sub(r'\s', '', text)
    
    if translate_engine == 'ali':
        # 定义匹配ALIMT占位符的正则表达式
        pattern = r'^(<ALIMT>PROTECTED\$\d+\$</ALIMT>)+$'
    elif translate_engine == 'ai':
        # 定义匹配PROTECTED${i}$占位符的正则表达式
        pattern = r'^(PROTECTED\$\d+\$)+$'
    else:
        raise ValueError(f"无效的翻译引擎: {translate_engine}")
    
    # 检查文本是否匹配正则表达式
    if re.match(pattern, text):
        return True
    else:
        return False

def restore_protected_text(text, placeholder_dict, is_contain_html_label):
    """
    恢复受保护的文本内容
    """
    if is_contain_html_label:
        for placeholder, original in placeholder_dict.items():
            text = text.replace(f"<ALIMT > {placeholder} </ALIMT>", original)
    else:
        for placeholder, original in placeholder_dict.items():
            text = text.replace(placeholder, original)
    return text


def merge_markdown_headers(para1, para2):
    # 去除段落开头和结尾的空白字符
    para1 = para1.strip()
    para2 = para2.strip()
    
    # 定义Markdown标题的正则表达式模式
    header_pattern = r'^(#{1,6})\s+(.+)$'
    
    # 尝试匹配两个段落
    match1 = re.match(header_pattern, para1)
    match2 = re.match(header_pattern, para2)
    
    # 如果两个段落都匹配成功
    if match1 and match2:
        # 提取标题级别和内容
        level1, content1 = match1.groups()
        level2, content2 = match2.groups()
        
        # 如果标题级别相同，合并内容
        if level1 == level2:
            return True, f"{level1} {content2}（{content1}）"
        else:
            # 如果标题级别不同，视为未成功合并
            return False, ""
    else:
        # 如果任一段落不是标题格式，视为未成功合并
        return False, ""


if __name__ == "__main__":
    # text, placeholder_dict = occupy_text(markdown_text2)
    # print(f"{text}\n\n{placeholder_dict}")

    # corrected_text = correct_markdown_syntax(" -  [LangChain Expression Language (LCEL)](/docs/how_to/#langchain-expression-language-lcel) ")
    # print(corrected_text)


#     test_cases = [
#         '<ALIMT > PROTECTED$13$ </ALIMT> <ALIMT > PROTECTED$6$ </ALIMT>',
#         '<ALIMT > PROTECTED$8$ </ALIMT> <ALIMT > PROTECTED$1$ </ALIMT>\n<ALIMT > PROTECTED$9$ </ALIMT> <ALIMT > PROTECTED$2$ </ALIMT>\n<ALIMT > PROTECTED$10$ </ALIMT> <ALIMT > PROTECTED$3$ </ALIMT>\n<ALIMT > PROTECTED$11$ </ALIMT> <ALIMT > PROTECTED$4$ </ALIMT>\n<ALIMT > PROTECTED$12$ </ALIMT> <ALIMT > PROTECTED$5$ </ALIMT>'
# ]
#     for i, case in enumerate(test_cases, 1):
#         result = is_fully_protected(case)
#         print(f"Test case {i}: {'Fully protected' if result else 'Not fully protected'}")
#         print(f"Input: {case}\n")

    test_cases = [
    ("## 标题\n", "## Title"),
    ("# 第一章\n", "## 1.1 节"),
    ("### 小节\n", "### Subsection"),
    ("正常段落", "## 标题"),
    ("  # 带空格的标题  ", "  # Title with spaces  "),
]

    for i, (para1, para2) in enumerate(test_cases, 1):
        print(f"测试用例 {i}:")
        print("输入:")
        print(f"段落1: {para1!r}")
        print(f"段落2: {para2!r}")
        print("输出:")
        print(merge_markdown_headers(para1, para2))
        print()






