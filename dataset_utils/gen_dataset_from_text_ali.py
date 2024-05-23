from openai import OpenAI
from jinja2 import Environment, FileSystemLoader


# 请将你的OpenAI API密钥替换为'YOUR_API_KEY'
api_key = 'sk-KCqYq2dpuMwmS8r46Tu8mdht8FMb55TfQUNdb1RpfrTkP1ec'
#base_url = 'https://api.openai-proxy.org/v1'
base_url = 'http://127.0.0.1:1234/v1'
DASHSCOPE_API_KEY ='sk-27c8ee79697f42c0a78e60ddd85ed712'
client = OpenAI(api_key=api_key,base_url=base_url)
# 加载模板文件
loader = FileSystemLoader('.')
env = Environment(loader=loader)
# 获取模板
template = env.get_template('mobile1.txt')
def get_response(question):
    client = OpenAI(
        api_key=DASHSCOPE_API_KEY, # 如果您没有配置环境变量，请在此处用您的API Key进行替换
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope SDK的base_url
    )
    completion = client.chat.completions.create(
        model="qwen1.5-32b-chat",
        messages=[{'role': 'system', 'content': 'You are a helpful assistant.'},
                  {'role': 'user', 'content': question}]
        )
    print(completion.choices[0].message.content)
    return(completion.choices[0].message.content)

def get_response_vs(question,model1,model2):
    client = OpenAI(
        api_key=DASHSCOPE_API_KEY, # 如果您没有配置环境变量，请在此处用您的API Key进行替换
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope SDK的base_url
    )
    completion1 = client.chat.completions.create(
        model=model1,
        messages=[{'role': 'system', 'content': 'You are a helpful assistant.'},
                  {'role': 'user', 'content': question}]
        )
    completion2 = client.chat.completions.create(
        model=model1,
        messages=[{'role': 'system', 'content': 'You are a helpful assistant.'},
                  {'role': 'user', 'content': question}]
        )
    return(completion1.choices[0].message.content,completion2.choices[0].message.content)


def parse_answer(answer):
    ans = answer.split('\n')
    print(ans)
    pairs = []
    i = 0
    while i < (len(ans)):
        pair = { "question":"", "answer":"" }
        if ans[i].startswith('Q:') and ans[i+1].startswith('A:'):
            pair["question"] = ans[i][2:]
            pair["answer"] = ans[i+1][2:]
            pairs.append(pair)
            i=i+1
        i=i+1
        
    return pairs
    
if __name__ == "__main__":
    anss = []
    for i in range(1, 3):
        user_input = template.render(title="中国移动无线网设备维护管理规定",pairs = anss)
        #answer = get_response(user_input)
        #array_answer = parse_answer(answer)
        #anss.extend(array_answer)
        answer1,answer2 = get_response_vs(user_input,"qwen1.5-32b-chat","qwen-turbo")
        array_answer1 = parse_answer(answer1)
        array_answer2 = parse_answer(answer2)
        anss.extend(array_answer1)
        anss.extend(array_answer2)
        
    
    for i in range(len(anss)):
        print(anss[i])