import argparse
import json
import logging
import sys
import os
from text import correct_markdown_syntax, is_fully_protected, merge_markdown_headers, occupy_text, restore_protected_text
from alibabacloud_translate import ali_translate
from ai_translate import ai_translate

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def translate_ipynb(input_file, translate_engine):
    # 读取输入的ipynb文件 
    with open(input_file, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
        
    total_cells = len(notebook['cells'])
    markdown_cells = sum(1 for cell in notebook['cells'] if cell['cell_type'] == 'markdown')
    logging.info(f"总单元格数: {total_cells}, Markdown单元格数: {markdown_cells}")

    # 处理笔记本中的每个单元格
    for cell_index, cell in enumerate(notebook['cells'], 1):
        if cell['cell_type'] == 'markdown':
            logging.info(f"正在处理单元格 {cell_index}/{total_cells} (Markdown)")
            
            # 将整个单元格的内容合并为一个字符串
            whole_cell_content = ''.join(cell['source'])
            
            try:
                # 对整个单元格内容应用occupy_text
                if translate_engine == 'ali':
                    protected_text, placeholder_dict = occupy_text(whole_cell_content, True)
                elif translate_engine == 'ai':
                    protected_text, placeholder_dict = occupy_text(whole_cell_content, False)
                
                # 将保护后的文本分割成段落
                protected_paragraphs = protected_text.split('\n\n')
                
                translated_source = []
                for paragraph_index, paragraph in enumerate(protected_paragraphs, 1):
                    # 跳过空段落
                    if not paragraph.strip():
                        logging.info(f"  跳过空段落 {paragraph_index}/{len(protected_paragraphs)}")
                        translated_source.append('\n')
                        continue
                    
                    logging.info(f"  正在翻译段落 {paragraph_index}/{len(protected_paragraphs)}")
                    
                    try:
                        # 恢复原始段落内容
                        if translate_engine == 'ali':
                            original_paragraph = restore_protected_text(paragraph, placeholder_dict, True)
                        elif translate_engine == 'ai':
                            original_paragraph = restore_protected_text(paragraph, placeholder_dict, False)

                        if is_fully_protected(paragraph, translate_engine):
                            logging.info("    段落完全由保护内容组成，跳过翻译, 直接使用原文")
                            translated_text = original_paragraph
                        else:
                            # 根据选择的翻译引擎进行翻译
                            if translate_engine == 'ali':
                                translated_text = ali_translate(paragraph)
                            elif translate_engine == 'ai':
                                translated_text = ai_translate(paragraph)
                            else:
                                raise ValueError(f"无效的翻译引擎: {translate_engine}")
                            
                            translated_text = restore_protected_text(translated_text, placeholder_dict, False)
                        
                            # 修正markdown语法
                            translated_text = correct_markdown_syntax(translated_text)

                        # 记录原文和译文
                        logging.info(f"    原文: {original_paragraph.strip()}")
                        logging.info(f"    占位: {paragraph.strip()}")
                        logging.info(f"    译文: {translated_text.strip()}")
                        
                        # 将恢复后的原文和译文添加到单元格
                        # 如果原文和译文相同（去掉前后空格后），则只添加原文
                        if original_paragraph.strip() == translated_text.strip():
                            translated_source.append(f"{original_paragraph}\n\n")
                        else:
                            # 尝试合并markdown标题
                            merge_headers_success,merge_headers_result = merge_markdown_headers(original_paragraph, translated_text)
                            # 如果合并成功，则原文和译文合并为一个段落
                            if merge_headers_success:
                                translated_source.append(f"{merge_headers_result}\n\n")
                            # 如果合并失败，添加原文和译文分别作为两个段落
                            else:
                                translated_source.append(f"{original_paragraph}\n\n{translated_text}\n\n")
                    except Exception as e:
                        logging.error(f"翻译段落时发生错误: {str(e)}")
                        logging.error(f"原文: {paragraph.strip()}")
                        # 如果翻译失败，保留原文
                        for placeholder, original in placeholder_dict.items():
                            paragraph = paragraph.replace(placeholder, original)
                        translated_source.append(paragraph + '\n')
                
                # 用原文和译文更新单元格内容
                cell['source'] = translated_source
            except Exception as e:
                logging.error(f"处理单元格时发生错误: {str(e)}")
                # 如果处理失败，保留原单元格内容
                cell['source'] = whole_cell_content.split('\n')
        else:
            logging.info(f"跳过单元格 {cell_index}/{total_cells} (非Markdown)")

    # 根据输入文件名生成输出文件名
    output_file = os.path.splitext(input_file)[0] + '_zh.ipynb'
    
    # 将翻译后的笔记本写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, ensure_ascii=False, indent=2)

    logging.info(f"翻译完成。输出已保存到 {output_file}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='将Jupyter Notebook中的Markdown单元格翻译为中文。')
    parser.add_argument('-e', '--engine', type=str, default='ali', choices=['ali', 'ai'],
                        help='选择翻译引擎: "ali" 表示阿里云翻译, "ai" 表示OpenAI翻译 (默认: "ali")')
    parser.add_argument('input_file', type=str, help='输入的Jupyter Notebook文件')
    
    args = parser.parse_args()
    
    input_file = args.input_file
    translate_engine = args.engine
    
    translate_ipynb(input_file, translate_engine)