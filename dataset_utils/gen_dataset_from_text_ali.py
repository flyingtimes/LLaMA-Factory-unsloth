from multiprocessing.connection import answer_challenge
from time import sleep
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader
import os,json,re,random
#   从配置文件读取环境变量
from dotenv import load_dotenv 
import pandas as pd
import argparse
parser = argparse.ArgumentParser(description="从文本到量化模型，使用qwen-32b-chat")
# 添加参数
parser.add_argument("-f",dest="filename",type=str, help="json格式的配置文件")
parser.add_argument("-t",dest="txtfilename",type=str, help="要学习的文本文件")
# 解析参数
args = parser.parse_args()

load_dotenv(verbose=True)

# 阿里云的配置信息
ali_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
# 本地lm-studio 配置
#base_url="http://127.0.0.1:1234/v1"
client = OpenAI(api_key=DASHSCOPE_API_KEY,base_url=ali_base_url)
# 加载模板文件
loader = FileSystemLoader('.')
env = Environment(loader=loader)

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
    while i+1 < (len(ans)):
        pair = { "question": "", "answer": "" }
        question = ans[i].strip()
        answer = ans[i+1].strip()
        if question.startswith('Q:') and answer.startswith('A:'):
            pair["question"] = question.strip("Q: ").strip("Q:").strip(" Q:").strip()
            pair["answer"] = answer.strip("A: ").strip("A:").strip(" A:").strip()
            print(pair)
            pairs.append(pair)
            i=i+1
        i=i+1
        
    return pairs
def summarize(atask,tasks):
    template = env.get_template(atask["args"]["template"])
    user_input = template.render(content=atask["args"]["content"])
    answer = get_response(user_input,"qwen-plus")
    return answer

def keynote(atask,tasks):
    template = env.get_template(atask["args"]["template"])
    for task in tasks:
        if task["task_name"] == "summarize_full":
            acontent = task["args"]["content"]
            break
    user_input = template.render(content=acontent)
    answer = get_response(user_input,"qwen-plus")
    print(answer)
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
                answer = get_response(user_input,"qwen-plus")
                print(keynote+answer)
                sleep(10)
                answers.append(keynote+answer)
                sleep(5)
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
                anss.extend(array_answer)
            return anss

def pairs_with_title(atask,tasks):
    template = env.get_template(atask["args"]["template"])
    template1 = env.get_template(atask["args"]["template1"])
    for task in tasks:
        if task["task_name"] == "pairs":
            atitle = atask["title"]
            results = task["result"]
            anss = []
            for result in results:
                question = result["question"]
                answer = result["answer"]
                user_input = template.render(content=question,title=atitle)
                question = get_response(user_input,"qwen-turbo")
                user_input = template1.render(content=answer,title=atitle)
                answer = get_response(user_input,"qwen-turbo")
                print({"question": question,"answer": answer})
                anss.append({"question": question,"answer": answer})
            return anss
        
def export_to_xls(atask,tasks):
    for task in tasks:
        if task["task_name"] == "pairs_with_title":
            results = task["result"]
            # 将JSON数组转换为DataFrame
            dataframes = [pd.DataFrame([item]) for item in results]
            df = pd.concat(dataframes, ignore_index=True)
            # 写入Excel文件
            df.to_excel(atask["filename"], index=False)
    atask["result"] = "ok"

def export_to_jsonl(atask,tasks):
    for task in tasks:
        if task["task_name"] == "pairs_with_title":
            results = task["result"]
            chatml_format_data = []
            for result in results:
                message = {"messages": [{"role": "system", "content": "You are a helpful assistant"}, {"role": "user", "content": result["question"]}, {"role": "assistant", "content": result["answer"]}]}
                chatml_format_data.append(message)
            with open(atask["filename"], 'w',encoding='utf-8') as f:
                for message in chatml_format_data:
                    json.dump(message, f)
                    f.write('\n')
            break
    atask["result"] = "ok"


def export_longchat_to_jsonl(atask,tasks):
    for mtask in tasks:
        if mtask["task_name"] == "pairs":
            mresults = mtask["result"]
            break
    for task in tasks:
        if task["task_name"] == "pairs_with_title":
            results = task["result"]
            chatml_format_data = []
            for result in results:
                #system_prompt = "<|im_start|>system\nYou are a helpful assistant<|im_end|>\n"
                #user_prompt =f"<|im_start|>user\n{result['question']}<|im_end|>\n"
                #assistant_prompt = f"<|im_start|>assistant\n{result['answer']}<|im_end|>"
                #message = system_prompt + user_prompt + assistant_prompt
                m = [{"role": "system", "content": "You are a helpful assistant."}]
                m.append({"role": "user", "content": result["question"]})
                m.append({"role": "assistant", "content": result["answer"]})
                message ={"messages":m}
                print(message)
                chatml_format_data.append(message)
            ## 多轮数据扩充
            for m in range(20):
                for h in range(2,7):
                    numbers = list(range(1, len(results)))
                    random.shuffle(numbers)
                    group_size = h # 每组的大小为h 个对话
                    for i in range(0, len(numbers), group_size):
                        group = numbers[i:i + group_size]
                        m = [{"role": "system", "content": "You are a helpful assistant."}]
                        #system_prompt = "<|im_start|>system\nYou are a helpful assistant<|im_end|>\n"
                        #user_prompt =f"<|im_start|>user\n{results[i]['question']}<|im_end|>\n"
                        #assistant_prompt = f"<|im_start|>assistant\n{mresults[i]['answer']}<|im_end|>\n"
                        #m = system_prompt + user_prompt + assistant_prompt
                        m.append({"role": "user", "content": results[i]["question"]})
                        m.append({"role": "assistant", "content": mresults[i]["answer"]})
                        for item in group:
                            #m += f"<|im_start|>user\n{mresults[i]['question']}<|im_end|>\n"
                            #m += f"<|im_start|>assistant\n{mresults[i]['answer']}<|im_end|>\n"
                            m.append({"role": "user", "content": mresults[item]["question"]})
                            m.append({"role": "assistant", "content": mresults[item]["answer"]})
                        message ={"messages":m}
                        chatml_format_data.append(message)
                        #chatml_format_data.append({"text":m})

            with open(atask["filename"], 'w', encoding='utf-8') as f:
                for message in chatml_format_data:
                    json.dump(message, f, ensure_ascii=False)
                    f.write('\n')
            break
    atask["result"] = "ok"

def read_json_from_file(filename):
    with open(filename, 'r',encoding='utf-8') as json_file:
        loaded_data = json.load(json_file)
    return loaded_data

def save_json(a_json,filename):
    with open(filename, 'w',encoding='utf-8') as json_file:
        json.dump(a_json, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    
    tasks = read_json_from_file(args.filename)
    with open(args.txtfilename, 'r', encoding='utf-8') as file:
        content = file.read()
    tasks[0]["args"]["content"] = content

    output = []
    for task in tasks:
        if task["result"]=="":
            print(f"正在执行的任务:{task['description']}")
            task["result"] = globals()[task["function_call"]](task,tasks)
        output.append(task)
    
    save_json(output,args.filename)
    # anss = []
    # for i in range(1, 5):
    #     user_input = template.render(title="中国移动无线网设备维护管理规定",pairs = anss)
    #     answer = get_response(user_input)
    #     array_answer = parse_answer(answer)
    #     anss.extend(array_answer)
        
    
    # for i in range(len(anss)):
    #     print(anss[i])