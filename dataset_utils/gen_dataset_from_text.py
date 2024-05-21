from openai import OpenAI
from jinja2 import Environment, FileSystemLoader

# 请将你的OpenAI API密钥替换为'YOUR_API_KEY'
api_key = 'sk-KCqYq2dpuMwmS8r46Tu8mdht8FMb55TfQUNdb1RpfrTkP1ec'
base_url = 'https://api.openai-proxy.org/v1'

client = OpenAI(api_key=api_key,base_url=base_url)
# 加载模板文件
loader = FileSystemLoader('.')
env = Environment(loader=loader)
# 获取模板
template = env.get_template('template.txt')

def answer_question(question):
    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": question}
    ]
    )

    return(completion.choices[0].message.content)

def parse_answer(answer):
    ans = answer.split('|')
    if len(ans) % 2 != 0:
        return []
    pairs = []
    i = 0
    while i < (len(ans)):
        pair = { "question":"", "answer":"" }
        pair["question"] = ans[i]
        pair["answer"] = ans[i+1]
        pairs.append(pair)
        i +=2

    return pairs
    
if __name__ == "__main__":
    ans = []
    for i in range(1, 5):
        user_input = template.render(title="金融机构管理办法",pairs = ans)
        answer = answer_question(user_input)
        ans.extend(parse_answer(answer))
    
    for i in range(len(ans)):
        print(ans[i])