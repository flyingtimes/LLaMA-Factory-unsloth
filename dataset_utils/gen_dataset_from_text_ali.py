from openai import OpenAI
from jinja2 import Environment, FileSystemLoader
import os,json,re
#   从配置文件读取环境变量
from dotenv import load_dotenv 
load_dotenv(".env")

# 阿里云的配置信息
ali_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

client = OpenAI(api_key=DASHSCOPE_API_KEY,base_url=ali_base_url)
# 加载模板文件
loader = FileSystemLoader('.')
env = Environment(loader=loader)
# 获取模板
template = env.get_template('mobile1.txt')
def get_response(question,modelname):
    MODEL_NAME = modelname
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{'role': 'system', 'content': 'You are a helpful assistant.'},
                  {'role': 'user', 'content': question}]
        )
    #print(completion)
    fee = 0.0
    if MODEL_NAME=='qwen1.5-32b-chat':
        fee = completion.usage.total_tokens/1000*0.007-completion.usage.prompt_tokens/1000*0.0035
    elif MODEL_NAME=='qwen-turbo':
        fee = completion.usage.total_tokens/1000*0.006-completion.usage.prompt_tokens/1000*0.002
    elif  MODEL_NAME=='qwen-plus':
        fee = completion.usage.total_tokens/1000*0.012-completion.usage.prompt_tokens/1000*0.004
    elif  MODEL_NAME=='qwen-max':
        fee = completion.usage.total_tokens/1000*0.12-completion.usage.prompt_tokens/1000*0.04
    elif MODEL_NAME=='qwen-long':
        fee = completion.usage.total_tokens/1000*0.002-completion.usage.prompt_tokens/1000*0.0005
    print(f"total tokens:{completion.usage.total_tokens}, total fee:{fee}")
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
def summarize(atask,tasks):
    template = env.get_template(atask["args"]["template"])
    user_input = template.render(content=atask["args"]["content"])
    answer = get_response(user_input,"qwen-long")
    return answer

def keynote(atask,tasks):
    template = env.get_template(atask["args"]["template"])
    for task in tasks:
        if task["task_name"] == "summarize_full":
            acontent = task["args"]["content"]
            break
    user_input = template.render(content=acontent)
    answer = get_response(user_input,"qwen-long")
    return answer

def category(atask,tasks):
    template = env.get_template(atask["args"]["template"])
    for task in tasks:
        if task["task_name"] == "summarize_full":
            acontent = task["args"]["content"]
            break
    ## 
    for task in tasks:
        if task["task_name"] == "keynote":
            akeynote = json.loads(task["result"])
            answers = []
            for keynote in akeynote:
                user_input = template.render(content=acontent,keynote=keynote)
                answer = get_response(user_input,"qwen-long")
                print(keynote+answer)
                answers.append(keynote+answer)
            return answers
            
    
def pairs(atask,tasks):
    template = env.get_template(atask["args"]["template"])
    for task in tasks:
        if task["task_name"] == "summarize_full":
            summarize = task["result"]
    for task in tasks:
        if task["task_name"] == "category":
            results = task["result"]
            atitle = atask["title"]
            anss = []
            for result in results:
                user_input = template.render(summary=summarize, content=result,title=atitle)
                answer = get_response(user_input,"qwen-turbo")
                array_answer = parse_answer(answer)
                print(array_answer)
                anss.extend(array_answer)
            return anss

    


def read_json_from_file(filename):
    with open(filename, 'r') as json_file:
        loaded_data = json.load(json_file)
    return loaded_data

def save_json(a_json,filename):
    with open(filename, 'w') as json_file:
        json.dump(a_json, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    
    tasks = read_json_from_file("task001.json")
    with open("mobile.txt", 'r', encoding='utf-8') as file:
        content = file.read()
    tasks[0]["args"]["content"] = content

    output = []
    for task in tasks:
        if task["result"]=="":
            print(f"正在执行的任务:{task['description']}")
            task["result"] = globals()[task["function_call"]](task,tasks)
        output.append(task)
    
    save_json(output,"task001.json")
    # anss = []
    # for i in range(1, 5):
    #     user_input = template.render(title="中国移动无线网设备维护管理规定",pairs = anss)
    #     answer = get_response(user_input)
    #     array_answer = parse_answer(answer)
    #     anss.extend(array_answer)
        
    
    # for i in range(len(anss)):
    #     print(anss[i])