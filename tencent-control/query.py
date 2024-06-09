import json
import types
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.hai.v20230812 import hai_client, models

import os,time
#   从配置文件读取环境变量
from dotenv import load_dotenv 
load_dotenv(verbose=True)
secid = os.environ.get('SECRETID')
seckey = os.environ.get('SECRETKEY')

def startInstance():
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
        # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
        cred = credential.Credential(secid, seckey)
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "hai.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = hai_client.HaiClient(cred, "ap-guangzhou", clientProfile)
        # start
        req = models.StartInstanceRequest()
        # close
        # 实例化一个请求对象,每个接口都会对应一个request对象
        #req = models.StopInstanceRequest()
        params = {
            "InstanceId": "hai-84zw63uv"
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个StopInstanceResponse的实例，与请求对象对应
        resp = client.StartInstance(req)
        #resp = client.StopInstance(req)
        # 输出json格式的字符串回包
        print(resp.to_json_string())
    except TencentCloudSDKException as err:
        print(err)

def getInstanceIP():
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
        # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
        cred = credential.Credential(secid, seckey)
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "hai.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = hai_client.HaiClient(cred, "ap-guangzhou", clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.DescribeInstancesRequest()
        params = {
            "InstanceIds": [ "hai-84zw63uv" ]
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个DescribeInstancesResponse的实例，与请求对象对应
        resp = client.DescribeInstances(req)
        # 输出json格式的字符串回包
        if resp.InstanceSet[0].InstanceState == "RUNNING":
            return resp.InstanceSet[0].PublicIpAddresses[0]
        return "unknown"
    except TencentCloudSDKException as err:
        print(err)

server_ip = getInstanceIP()
if server_ip == "unknown":
    startInstance()
    print("starting service,please wait...")
    time.sleep(40)
    server_ip = getInstanceIP()
print(server_ip)

import requests
atext = '''
我喜欢第二种类型的，你帮我挑个合适的。
'''
url = f"http://{server_ip}:9966/tts"
print(url)
res = requests.post(url, data={
  "type": 1,
  "text": atext,
  "prompt": "[oral_3][laugh_0][break_5]",
  "voice": "2",
  "temperature": 0.7,
  "top_p": 0.7,
  "top_k": 20,
  "skip_refine": 0,
  "is_split": 1
})
result = res.json()
print(result['audio_files'][0]['url_mp3'])