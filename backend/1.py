import fitz  # PyMuPDF
import re
import pandas as pd
import os

try:
    # PDF 文件路径
    pdf_path = "德国农业概况.pdf"
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
    
    doc = fitz.open(pdf_path)

    # 1. 提取文本内容
    all_text = ""
    for page in doc:
        page_text = page.get_text("text")
        all_text += page_text + "\n"

    # 保存全文
    try:
        with open("extracted_text.txt", "w", encoding="utf-8") as f:
            f.write(all_text)
        print("全文已提取并保存到 extracted_text.txt")
    except Exception as e:
        print(f"保存文本文件失败: {e}")

    # 拆分段落
    paragraphs = [para.strip() for para in all_text.split("\n\n") if para.strip()]
    print(f"提取到的段落数量: {len(paragraphs)}")

    # 2. 提取表格
    all_tables = []
    
    for page_num, page in enumerate(doc):
        try:
            if hasattr(page, 'find_tables'):
                tables = page.find_tables()
                for tbl in tables:
                    table_data = tbl.extract()
                    if table_data and len(table_data) > 1:
                        df = pd.DataFrame(table_data[1:], columns=table_data[0])
                        all_tables.append(df)
            else:
                print("当前PyMuPDF版本不支持表格检测功能")
        except Exception as e:
            print(f"处理第 {page_num + 1} 页表格时出错: {e}")

    print(f"总共检测到 {len(all_tables)} 个表格。")

    # 保存表格
    for idx, df in enumerate(all_tables):
        try:
            if not df.empty:
                csv_filename = f"table_{idx+1}.csv"
                df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                print(f"表格 {idx+1} 已保存为 {csv_filename}")
        except Exception as e:
            print(f"保存表格 {idx+1} 时出错: {e}")

    # 3. 提取数字信息
    percent_pattern = re.compile(r"\d+(?:\.\d+)?%")
    currency_pattern = re.compile(r"[$¥€]\s?\d[\d,]*(?:\.\d+)?")
    number_pattern = re.compile(r"\b\d+(?:\.\d+)?\b")

    percentages = percent_pattern.findall(all_text)
    currencies = currency_pattern.findall(all_text)
    numbers = number_pattern.findall(all_text)

    print("\n数据统计:")
    print(f"找到的百分比: {len(percentages)} 个")
    print(f"找到的货币金额: {len(currencies)} 个")
    print(f"找到的数字: {len(numbers)} 个")

except Exception as e:
    print(f"程序执行出错: {e}")

finally:
    if 'doc' in locals():
        doc.close()