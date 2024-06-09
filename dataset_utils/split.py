import random

# 打开源文件
with open('data/all_data.jsonl', 'r') as source_file:
    lines = source_file.readlines()

# 计算90%和10%的行数
split_point = int(len(lines) * 0.9)
print(f"正在生成{split_point}条训练数据。。。")
# 随机打乱行的顺序
random.shuffle(lines)

# 写入90%的行到第一个文件
with open('data/train.jsonl', 'w') as file1:
    for line in lines[:split_point]:
        file1.write(line)

# 写入剩下的10%的行到第二个文件
with open('data/valid.jsonl', 'w') as file2:
    for line in lines[split_point:]:
        file2.write(line)