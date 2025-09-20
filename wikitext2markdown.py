import re
import os

def wikitext_table_to_markdown(wikitext):
    lines = wikitext.strip().split('\n')
    rows = []
    for line in lines:
        if line.startswith('{|') or line.startswith('|}'):
            continue
        if line.startswith('|-'):
            continue
        if line.startswith('|'):
            # 去掉开头的 |
            cells = [cell.strip() for cell in re.split(r'\|\|', line[1:])]
            rows.append(cells)
    # 构造 markdown 表格
    md = []
    if rows:
        # 表头
        md.append('| ' + ' | '.join(rows[0]) + ' |')
        md.append('|' + '---|' * len(rows[0]))
        # 表体
        for row in rows[1:]:
            md.append('| ' + ' | '.join(row) + ' |')
    return '\n'.join(md)

def wikitext_to_markdown(text):
    # 先处理所有表格段落
    def table_replacer(match):
        return wikitext_table_to_markdown(match.group(0))

    # 匹配所有wikitext表格段落
    text = re.sub(r'{\|[\s\S]+?\|}', table_replacer, text)

    # 列表
    text = re.sub(r'^\* (.*)', r'- \1', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*)', r'1. \1', text, flags=re.MULTILINE)
    
    # 标题
    text = re.sub(r'={1,6}\s*(.+?)\s*={1,6}', lambda m: '#' * (m.group(0).count('=') // 2) + ' ' + m.group(1), text)
    # 粗体
    text = re.sub(r"'''(.*?)'''", r'**\1**', text)
    # 斜体
    text = re.sub(r"''(.*?)''", r'*\1*', text)
    # 链接
    text = re.sub(r'\[\[([^\|\]]+)\|([^\]]+)\]\]', r'[\2](\1)', text)
    text = re.sub(r'\[\[([^\]]+)\]\]', r'[\1](\1)', text)

    # 引用
    text = re.sub(r'^:(.*)', r'> \1', text, flags=re.MULTILINE)
    # 行内代码
    text = re.sub(r'<code>(.*?)</code>', r'`\1`', text)
    # 图片/文件
    text = re.sub(r'\[\[File:([^\|\]]+)\|([^\]]+)\]\]', r'![\2](\1)', text)
    return text

def convert_folder(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for filename in os.listdir(input_folder):
        if filename.endswith('.text'):
            with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as f:
                wikitext = f.read()
            markdown = wikitext_to_markdown(wikitext)
            outname = filename.replace('.text', '.md')
            with open(os.path.join(output_folder, outname), 'w', encoding='utf-8') as f:
                f.write(markdown)

if __name__ == '__main__':
    # 接受input 和output参数，并处理的代码
    import argparse
    parser = argparse.ArgumentParser(description='Convert MediaWiki text files to Markdown.')
    parser.add_argument('--input', '-i', default='pages', help='Input directory containing .text files')
    parser.add_argument('--output', '-o', default='pages_md', help='Output directory for .md files')
    args = parser.parse_args()

    input_dir = args.input
    output_dir = args.output
    convert_folder(input_dir, output_dir)