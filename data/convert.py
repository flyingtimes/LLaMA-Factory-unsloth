import json

def convert_to_chatml(json_data):
    chatml_format_data = []
    for dialogue in json_data:
        chatml_dialogue = f"<|im_start|>system\nYou are a helpful assistant<|im_end|>\n<|im_start|>user\n{dialogue['instruction']}<|im_end|>\n|im_start|>assistant\n{dialogue['output']}<|im_end|>"
        chatml_format_data.append({"text": chatml_dialogue})
    return chatml_format_data

def write_to_jsonl(data, output_file):
    with open(output_file, 'w') as f:
        for dialogue in data:
            json.dump(dialogue, f)
            f.write('\n')

# 读取alpaca的JSON数据
with open('identity_cgm.json', 'r',encoding='utf-8') as f:
    alpaca_data = json.load(f)

# 转换数据格式
chatml_data = convert_to_chatml(alpaca_data)

# 将转换后的数据写入JSONL文件
write_to_jsonl(chatml_data, 'identity_cgm.jsonl')