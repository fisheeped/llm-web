import re
import json
import json5

def get_repair_json(json_str) -> dict:
    # clean json str from model 
    json_str = f"{'{'}{json_str.split('{',1)[-1].rsplit('}',1)[0]}{'}'}"
    try:
        # loads json directly
        return json5.loads(json_str)
    except json.JSONDecodeError:
        # try to repair by del comma
        while True:
            new_json = re.sub(r',\s*([\]}])', r'\1', json_str)
            if new_json == json_str:
                break
            json_str = new_json
        try:
            return json5.loads(json_str)
        except json.JSONDecodeError:
            return {}
def get_repair_list(data_str):
    # str(list) to list
    # 去掉前后的方括号
    pattern = r"\['(.*?)'\]"
    data_str = re.findall(pattern, data_str)[0]
    data_str = data_str.replace("'",'')
    data_str = data_str.replace('"','')
    # 使用正则表达式匹配内容
    pattern = re.compile(r'"(.*?)"|([^,]+)')
    matches = pattern.findall(data_str)

    # 提取匹配结果并去掉多余的空格
    data_list = [match[0].strip() if match[0] else match[1].strip() for match in matches]

    return data_list

def add_comment(sql:str,added_key:str,added_comment:str):
    # 需要追加的字符串
    pattern = re.compile(f"(`{added_key}`.*?COMMENT ')(.*?)(')", re.DOTALL)
    # 替换 COMMENT 部分
    new_sql = pattern.sub(r"\1" + added_comment + r"\3", sql)
    return new_sql

def cleaned_sql_id(sql):
    # 只删除 _id`,\n的情况
    pattern = re.compile(r'\s*.*(_ID|_id).*,\n', re.IGNORECASE)
    cleaned_sql = pattern.sub('', sql)
    return cleaned_sql

def add_prompt(prompt:str,added_key:str,added_comment:str):
    if added_key in prompt:
        prompt = f"{prompt}{added_comment}"


def getcode(data,mode = ""):
    code_str = None
    groups = re.search(f'```{mode}.*?\n(.*?)```', data, re.DOTALL)
    if groups:
        code_str = groups.group(1).strip()
    return code_str



def _parse_text(text):
    lines = text.split('\n')
    lines = [line for line in lines if line != '']
    count = 0
    for i, line in enumerate(lines):
        if '```' in line:
            count += 1
            items = line.split('`')
            if count % 2 == 1:
                lines[i] = f'<pre><code class="language-{items[-1]}">'
            else:
                lines[i] = '<br></code></pre>'
        else:
            if i > 0:
                if count % 2 == 1:
                    line = line.replace('`', r'\`')
                    line = line.replace('<', '&lt;')
                    line = line.replace('>', '&gt;')
                    line = line.replace(' ', '&nbsp;')
                    line = line.replace('*', '&ast;')
                    line = line.replace('_', '&lowbar;')
                    line = line.replace('-', '&#45;')
                    line = line.replace('.', '&#46;')
                    line = line.replace('!', '&#33;')
                    line = line.replace('(', '&#40;')
                    line = line.replace(')', '&#41;')
                    line = line.replace('$', '&#36;')
                lines[i] = '<br>' + line
    text = ''.join(lines)
    return text