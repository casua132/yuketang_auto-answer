import os
import requests
import threading
import random
import time
import websocket
import json
from Scripts.Utils import get_user_info, dict_result, calculate_waittime
# from volcenginesdkarkruntime import Ark  # Removed dependency
from dotenv import load_dotenv
import base64

# 加载 .env 文件
load_dotenv()

# Simplified client that uses requests directly
class SimpleArkClient:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.models = self.Models(self)

    class Models:
        def __init__(self, client):
            self.completions = self.Completions(client)
        
        class Completions:
            def __init__(self, client):
                self.client = client
                
            def create(self, model, messages, extra_body=None):
                url = f"{self.client.base_url}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.client.api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": model,
                    "messages": messages
                }
                if extra_body:
                    data.update(extra_body)
                    
                response = requests.post(url, headers=headers, json=data, timeout=60)
                if response.status_code == 200:
                    return self.Response(response.json())
                else:
                    print(f"Error calling AI: {response.text}")
                    raise Exception(f"API Error: {response.status_code} {response.text}")

            class Response:
                def __init__(self, data):
                    self.choices = [self.Choice(c) for c in data.get("choices", [])]
                
                class Choice:
                    def __init__(self, data):
                        self.message = self.Message(data.get("message", {}))
                    
                    class Message:
                        def __init__(self, data):
                            self.content = data.get("content", "")

# Launch deepseek
client = None

def get_client(api_key):
    global client
    if client:
        return client
    if api_key:
        try:
            # client = Ark(api_key=api_key, base_url="https://ark.cn-beijing.volces.com/api/v3",)
            client = SimpleArkClient(api_key=api_key, base_url="https://ark.cn-beijing.volces.com/api/v3")
            return client
        except Exception as e:
            print(f"Client init error: {e}")
            return None
    return None

wss_url = "wss://www.yuketang.cn/wsapp/"
class Lesson:
    def __init__(self,lessonid,lessonname,classroomid,main_ui):
        self.classroomid = classroomid
        self.lessonid = lessonid
        self.lessonname = lessonname
        self.sessionid = main_ui.config["sessionid"]
        self.headers = {
            "Cookie":"sessionid=%s" % self.sessionid,
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
        }
        self.receive_danmu = {}
        self.sent_danmu_dict = {}
        self.danmu_dict = {}
        self.problems_ls = []
        self.unlocked_problem = []
        self.classmates_ls = []
        self.add_message = main_ui.add_message_signal.emit
        self.add_course = main_ui.add_course_signal.emit
        self.del_course = main_ui.del_course_signal.emit
        self.config = main_ui.config
        code, rtn = get_user_info(self.sessionid)
        self.user_uid = rtn["id"]
        self.user_uname = rtn["name"]
        self.main_ui = main_ui
        self.lesson_finished = False

    def _get_ppt(self,presentationid):
        # 获取课程各页ppt
        r = requests.get(url="https://www.yuketang.cn/api/v3/lesson/presentation/fetch?presentation_id=%s" % (presentationid),headers=self.headers,proxies={"http": None,"https":None})
        return dict_result(r.text)["data"]

    def get_problems(self,presentationid):
        # 获取课程ppt中的题目
        data = self._get_ppt(presentationid)
        #problem_slides = [problem for problem in data["slides"] if "problem" in problem.keys()]
        problems = []

        for problem in data["slides"]: 
            if "problem" in problem.keys():
                problem["problem"]["cover"] = problem.get("cover")
                problem["problem"]["coverAlt"] = problem.get("coverAlt")
                problem["problem"]["thumbnail"] = problem.get("thumbnail")
                problems.append(problem["problem"])

        # print("problem slide:\n")
        # print(problem_slides)   # if it appeared that there are some links(maybe about graph of problems), solutions will appear.
        # print("\nSlides of problems Over\n")

        # print("All problems in slides:\n")
        # for problem in problems:
        #    print(problem)
        #    print("\n")

        return problems

    def answer_questions(self,problemid,problemtype,answer,limit):
        # 回答问题
        answer_printed = answer
        if problemtype == 5:
            answer_printed = answer["content"]
        if answer and problemtype != 3:
            wait_time = calculate_waittime(limit, self.config["answer_config"]["answer_delay"]["type"], self.config["answer_config"]["answer_delay"]["custom"]["time"])
            if wait_time != 0:
                meg = "%s检测到问题，将在%s秒后自动回答，答案为%s" % (self.lessonname,wait_time,answer_printed)
                # threading.Thread(target=say_something,args=(meg,)).start()
                self.add_message(meg,3)
                time.sleep(wait_time)
            else:
                meg = "%s检测到问题，剩余时间小于15秒，将立即自动回答，答案为%s" % (self.lessonname,answer_printed)
                self.add_message(meg,3)
                # threading.Thread(target=say_something,args=(meg,)).start()
            data = {"problemId":problemid,"problemType":problemtype,"dt":int(time.time()),"result":answer}
            r = requests.post(url="https://www.yuketang.cn/api/v3/lesson/problem/answer",headers=self.headers,data=json.dumps(data),proxies={"http": None,"https":None})
            return_dict = dict_result(r.text)
            if return_dict["code"] == 0:
                meg = "%s自动回答成功" % self.lessonname
                self.add_message(meg,4)
                # threading.Thread(target=say_something,args=(meg,)).start()
                return True
            else:
                meg = "%s自动回答失败，原因：%s" % (self.lessonname,return_dict["msg"].replace("_"," "))
                self.add_message(meg,4)
                # threading.Thread(target=say_something,args=(meg,)).start()
                return False
        else:
            if limit == -1:
                meg = "%s的问题没有找到答案，该题不限时，请尽快前往雨课堂回答" % (self.lessonname)
            else:
                meg = "%s的问题没有找到答案，请在%s秒内前往雨课堂回答" % (self.lessonname,limit)
            # threading.Thread(target=say_something,args=(meg,)).start()
            self.add_message(meg,4)
            return False
    
    def on_open(self, wsapp):
        self.handshark = {"op":"hello","userid":self.user_uid,"role":"student","auth":self.auth,"lessonid":self.lessonid}
        wsapp.send(json.dumps(self.handshark))

    def checkin_class(self):
        r = requests.post(url="https://www.yuketang.cn/api/v3/lesson/checkin",headers=self.headers,data=json.dumps({"source":5,"lessonId":self.lessonid}),proxies={"http": None,"https":None})
        set_auth = r.headers.get("Set-Auth",None)
        times = 1
        while not set_auth and times <= 3:
            set_auth = r.headers.get("Set-Auth",None)
            times += 1
            time.sleep(1)
        self.headers["Authorization"] = "Bearer %s" % set_auth
        return dict_result(r.text)["data"]["lessonToken"]

    def on_message(self, wsapp, message):
        data = dict_result(message)
        op = data["op"]
        if op == "hello":
            presentations = list(set([slide["pres"] for slide in data["timeline"] if slide["type"]=="slide"]))
            current_presentation = data["presentation"]
            if current_presentation not in presentations:
                presentations.append(current_presentation)
            for presentationid in presentations:
                self.problems_ls.extend(self.get_problems(presentationid))
            self.unlocked_problem = data["unlockedproblem"]
            for problemid in self.unlocked_problem:
                self._current_problem(wsapp, problemid)
        elif op == "unlockproblem":
            self.start_answer(data["problem"]["sid"],data["problem"]["limit"])
        elif op == "lessonfinished":
            meg = "%s下课了" % self.lessonname
            # threading.Thread(target=say_something,args=(meg,)).start()
            self.add_message(meg,7)
            self.lesson_finished = True
            wsapp.close()
        elif op == "presentationupdated":
            self.problems_ls.extend(self.get_problems(data["presentation"]))
        elif op == "presentationcreated":
            self.problems_ls.extend(self.get_problems(data["presentation"]))
        elif op == "newdanmu" and self.config["auto_danmu"]:
            current_content = data["danmu"].lower()
            uid = data["userid"]
            sent_danmu_user = User(uid)
            if sent_danmu_user in self.classmates_ls:
                for i in self.classmates_ls:
                    if i == sent_danmu_user:
                        meg = "%s课程的%s%s发送了弹幕：%s" %(self.lessonname,i.sno,i.name,data["danmu"])
                        self.add_message(meg,2)
                        break
            else:
                self.classmates_ls.append(sent_danmu_user)
                sent_danmu_user.get_userinfo(self.classroomid,self.headers)
                meg = "%s课程的%s%s发送了弹幕：%s" %(self.lessonname,sent_danmu_user.sno,sent_danmu_user.name,data["danmu"])
                self.add_message(meg,2)
            now = time.time()
            # 收到一条弹幕，尝试取出其之前的所有记录的列表，取不到则初始化该内容列表
            try:
                same_content_ls = self.danmu_dict[current_content]
            except KeyError:
                self.danmu_dict[current_content] = []
                same_content_ls = self.danmu_dict[current_content]
            # 清除超过60秒的弹幕记录
            for i in same_content_ls:
                if now - i > 60:
                    same_content_ls.remove(i)
            # 如果当前的弹幕没被发过，或者已发送时间超过60秒
            if current_content not in self.sent_danmu_dict.keys() or now - self.sent_danmu_dict[current_content] > 60:
                if len(same_content_ls) + 1 >= self.config["danmu_config"]["danmu_limit"]:
                    self.send_danmu(current_content)
                    same_content_ls = []
                    self.sent_danmu_dict[current_content] = now
                else:
                    same_content_ls.append(now)
        elif op == "callpaused":
            meg = "%s点名了，点到了：%s" % (self.lessonname, data["name"])
            if self.user_uname == data["name"]:
                self.add_message(meg,5)
            else:
                self.add_message(meg,6)
        # 程序在上课中途运行，由_current_problem发送的已解锁题目数据，得到的返回值。
        # 此处需要筛选未到期的题目进行回答。
        elif op == "probleminfo":
            if data["limit"] != -1:
                time_left = int(data["limit"]-(int(data["now"]) - int(data["dt"]))/1000)
            else:
                time_left = data["limit"]
            # 筛选未到期题目
            if time_left > 0 or time_left == -1:
                if self.config["auto_answer"]:
                    self.start_answer(data["problemid"],time_left)
                else:
                    if time_left == -1:
                        meg = "%s检测到问题，该题不限时，请尽快前往雨课堂回答" % (self.lessonname)
                        self.add_message(meg,3)
                    else:
                        meg = "%s检测到问题，请在%s秒内前往雨课堂回答" % (self.lessonname,time_left)

    def start_answer(self, problemid, limit):
        for promble in self.problems_ls:

            #print("Problem to be solved\n")
            #print(promble)
           #  print("\n")  

            if promble["problemId"] == problemid:
                if promble["result"] is not None:
                    # 如果该题已经作答过，直接跳出函数以忽略该题
                    # 该情况理论上只会出现在启动监听时
                    return
                #blanks = promble.get("blanks",[])
                answers = []
                #if blanks:
                #    for i in blanks:
                #        answers.append(random.choice(i["answers"]))
                #else:
                answers = answer_through_gemini(promble)
                threading.Thread(target=self.answer_questions,args=(promble["problemId"],promble["problemType"],answers,limit)).start()
                break
        else:
            if limit == -1:
                meg = "%s的问题没有找到答案，该题不限时，请尽快前往雨课堂回答" % (self.lessonname)
            else:
                meg = "%s的问题没有找到答案，请在%s秒内前往雨课堂回答" % (self.lessonname,limit)
            self.add_message(meg,4)
            # threading.Thread(target=say_something,args=(meg,)).start()

    
    def _current_problem(self, wsapp, promblemid):
        # 为获取已解锁的问题详情信息，向wsapp发送probleminfo
        query_problem = {"op":"probleminfo","lessonid":self.lessonid,"problemid":promblemid,"msgid":1}
        wsapp.send(json.dumps(query_problem))
    
    def start_lesson(self, callback):
        self.auth = self.checkin_class()
        rtn = self.get_lesson_info()
        teacher = rtn["teacher"]["name"]
        title = rtn["title"]
        timestamp = rtn["startTime"] // 1000
        time_str = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(timestamp))
        index = self.main_ui.tableWidget.rowCount()
        # Pass lessonid as part of the data or separate argument if possible, 
        # but the original add_course expects a list and index.
        # We will modify add_course to accept lessonid in the list or handle it.
        # Actually, let's just use lessonid for deletion.
        self.add_course([self.lessonname,title,teacher,time_str,self.lessonid],index)

        while self.main_ui.is_active and not self.lesson_finished:
             # Re-create WebSocketApp instance for each connection attempt to ensure clean state
             self.wsapp = websocket.WebSocketApp(url=wss_url,header=self.headers,on_open=self.on_open,on_message=self.on_message)
             self.wsapp.run_forever(ping_interval=30, ping_timeout=10)

             # If it exits but not finished and still active, wait a bit and reconnect
             if self.main_ui.is_active and not self.lesson_finished:
                 meg = "%s连接断开，尝试重连..." % self.lessonname
                 self.add_message(meg, 8)
                 time.sleep(3)

        meg = "%s监听结束" % self.lessonname
        self.add_message(meg,7)
        self.del_course(self.lessonid)
        # threading.Thread(target=say_something,args=(meg,)).start()
        return callback(self)
    
    def send_danmu(self,content):
        url = "https://www.yuketang.cn/api/v3/lesson/danmu/send"
        data = {
            "extra": "",
            "fromStart": "50",
            "lessonId": self.lessonid,
            "message": content,
            "requiredCensor": False,
            "showStatus": True,
            "target": "",
            "userName": "",
            "wordCloud": True
        }
        r = requests.post(url=url,headers=self.headers,data=json.dumps(data),proxies={"http": None,"https":None})
        if dict_result(r.text)["code"] == 0:
            meg = "%s弹幕发送成功！内容：%s" % (self.lessonname,content)
        else:
            meg = "%s弹幕发送失败！内容：%s" % (self.lessonname,content)
        self.add_message(meg,1)
    
    def get_lesson_info(self):
        url = "https://www.yuketang.cn/api/v3/lesson/basic-info"
        r = requests.get(url=url,headers=self.headers,proxies={"http": None,"https":None})
        return dict_result(r.text)["data"]
        

    def __eq__(self, other):
        return self.lessonid == other.lessonid

class User:
    def __init__(self, uid):
        self.uid = uid
    
    def get_userinfo(self, classroomid, headers):
        r = requests.get("https://www.yuketang.cn/v/course_meta/fetch_user_info_new?query_user_id=%s&classroom_id=%s" % (self.uid,classroomid),headers=headers,proxies={"http": None,"https":None})
        data = dict_result(r.text)["data"]
        self.sno = data["school_number"]
        self.name = data["name"]

def answer_through_gemini(promble):
    """
    """
    global client
    if client is None:
        api_key = os.environ.get("DOUBAO_API_KEY")
        if api_key:
            get_client(api_key)
        else:
            print("No API Key found in environment variables.")
            return None

    print("Begin to deal with problems")
    print(promble)
    print('\n')

    problemType = promble['problemType']
    body = promble['body']
    options = promble.get('options')
    options_formatted = ""
    cover = promble["cover"]
    coverAlt = promble["coverAlt"]
    thumbnail = promble["thumbnail"]
    urls = [cover, coverAlt, thumbnail]

    if options:
        for option in options:
            options_formatted += option['key'] + " : " + option['value'] + ". "

    # get coverage
    coverages = []
    for url in urls:
        response = requests.get(url)

        if response.status_code == 200 and "image" in response.headers.get("Content-Type", ""):
            image = base64.b64encode(response.content).decode("utf-8")
            coverages.append(image)
        else:
            print("下载失败：", response.status_code, response.headers.get("Content-Type"))

    answers = []

    model = "doubao-seed-1-6-vision-250815"

    if coverages:
        if options:
            if problemType == 1:
                # contents = [coverages[0], f"(上面为该题的图片描述)请回答下述问题(你只需要给出选择结果（即你的回答只能含有选项符号(例如若答案是C，则你的返回内容应该为'C')，不能含有其他内容， 单选题)： {body}, 选项为: {options_formatted}. 请给出答案"]
                messages = [
                    {
                        "role": "user",  
                        "content": [   
                            # 图片信息，希望模型理解的图片
                            {"type": "image_url", "image_url": {"url":  f"data:image/jpeg;base64,{coverages[0]}"},},
                            # 文本消息，希望模型根据图片信息回答的问题
                            {"type": "text", "text": f"(上面为该题的图片描述)请回答下述问题(你只需要给出选择结果（即你的回答只能含有选项符号(例如若答案是C，则你的返回内容应该为'C')，不能含有其他内容， 单选题)： {body}, 选项为: {options_formatted}. 请给出答案"}, 
                        ]
                    }
                ]
            else:
                # contents = [coverages[0], f"(上面为该题的图片描述)请回答下述问题(你只需要给出选择结果（即你的回答只能含有选项符号(例如若答案是ABC，则你的返回内容应该为'ABC')，不能含有其他内容， 多选题)： {body}, 选项为: {options_formatted}. 请给出答案"]
                messages = [
                    {
                        "role": "user",  
                        "content": [   
                            # 图片信息，希望模型理解的图片
                            {"type": "image_url", "image_url": {"url":  f"data:image/jpeg;base64,{coverages[0]}"},},
                            # 文本消息，希望模型根据图片信息回答的问题
                            {"type": "text", "text":  f"(上面为该题的图片描述)请回答下述问题(你只需要给出选择结果（即你的回答只能含有选项符号(例如若答案是ABC，则你的返回内容应该为'ABC')，不能含有其他内容， 多选题)： {body}, 选项为: {options_formatted}. 请给出答案"}, 
                        ]
                    }
                ]
        else:
            # contents = [coverages[0], f"(上面为该题的图片描述)请回答下述问题(你只需要给出题目要求回答的内容(例如：5+2=[]， 那么你的答案应该是'7'， 若有多个填空，则每个填空的答案间用','(英文字符的逗号分隔)不能含有其他内容)(只需要给出答案，不需要多余的解释）： {body}. 请给出答案"]
            messages = [
                    {
                        "role": "user",  
                        "content": [   
                            # 图片信息，希望模型理解的图片
                            {"type": "image_url", "image_url": {"url":  f"data:image/jpeg;base64,{coverages[0]}"},},
                            # 文本消息，希望模型根据图片信息回答的问题
                            {"type": "text", "text": f"(上面为该题的图片描述)请回答下述问题(你只需要给出题目要求回答的内容(例如：5+2=[]， 那么你的答案应该是'7'， 若有多个填空，则每个填空的答案间用'|'分隔(不能含有其他内容))。只需要给出答案，不需要多余的解释： {body}. 请给出答案"}, 
                        ]
                    }
                ]
        
        try:
            response = client.models.completions.create(
                model=model,
                messages=messages,
                extra_body={
                    "thinking": {
                        "type": "disabled"  # 不使用深度思考能力
                        # "type": "enabled" # 使用深度思考能力
                        # "type": "auto" # 模型自行判断是否使用深度思考能力
                    }
                },
            )
        except Exception as e:
            print(f"AI Request Failed: {e}")
            return None
    else:
        if options:
            if problemType == 1:
                # contents = [coverages[0], f"(上面为该题的图片描述)请回答下述问题(你只需要给出选择结果（即你的回答只能含有选项符号(例如若答案是C，则你的返回内容应该为'C')，不能含有其他内容， 单选题)： {body}, 选项为: {options_formatted}. 请给出答案"]
                messages = [
                    {
                        "role": "user",  
                        "content": [   
                            # 文本消息，希望模型根据图片信息回答的问题
                            {"type": "text", "text": f"请回答下述问题(你只需要给出选择结果（即你的回答只能含有选项符号(例如若答案是C，则你的返回内容应该为'C')，不能含有其他内容， 单选题)(若经分析题目需要图片才可解答而我没有给你，请忽略上文我的要求，然后你的回答应该是'Image Missing', 不含其他)： {body}, 选项为: {options_formatted}. 请给出答案"}, 
                        ]
                    }
                ]
            else:
                # contents = [coverages[0], f"(上面为该题的图片描述)请回答下述问题(你只需要给出选择结果（即你的回答只能含有选项符号(例如若答案是ABC，则你的返回内容应该为'ABC')，不能含有其他内容， 多选题)： {body}, 选项为: {options_formatted}. 请给出答案"]
                messages = [
                    {
                        "role": "user",  
                        "content": [   
                            # 文本消息，希望模型根据图片信息回答的问题
                            {"type": "text", "text": f"请回答下述问题(你只需要给出选择结果（即你的回答只能含有选项符号(例如若答案是ABC，则你的返回内容应该为'ABC')，不能含有其他内容， 多选题)(若经分析题目需要图片才可解答而我没有给你，请忽略上文我的要求，然后你的回答应该是'Image Missing', 不含其他)： {body}, 选项为: {options_formatted}. 请给出答案"}, 
                        ]
                    }
                ]
        else:
            # contents = [coverages[0], f"(上面为该题的图片描述)请回答下述问题(你只需要给出题目要求回答的内容(例如：5+2=[]， 那么你的答案应该是'7'， 若有多个填空，则每个填空的答案间用','(英文字符的逗号)分隔)不能含有其他内容)： {body}. 请给出答案"]
            messages = [
                    {
                        "role": "user",  
                        "content": [   
                            # 文本消息，希望模型根据图片信息回答的问题
                            {"type": "text", "text": f"请回答下述问题(你只需要给出题目要求回答的内容(例如：5+2=[]， 那么你的答案应该是'7'， 若有多个填空，则每个填空的答案间用'|'分隔(不能含有其他内容))。只需要给出答案，不需要多余的解释(若经分析题目需要图片才可解答而我没有给你，请忽略上文我的要求，然后你的回答应该是'Image Missing', 不含其他)： {body}. 请给出答案"}, 
                        ]
                    }
                ]
        
        try:
            response = client.models.completions.create(
                model=model,
                messages=messages,
                extra_body={
                    "thinking": {
                        "type": "disabled"  # 不使用深度思考能力
                        # "type": "enabled" # 使用深度思考能力
                        # "type": "auto" # 模型自行判断是否使用深度思考能力
                    }
                },
            )
        except Exception as e:
            print(f"AI Request Failed: {e}")
            return None

    if response.choices[0].message.content == "Image Missing":
        return None
        
    print("The answers of model:")
    print(response.choices[0].message.content)

    if options:
        if problemType == 1:
            answers.append(response.choices[0].message.content)
        else:
            for c in response.choices[0].message.content:
                answers.append(c)
    else:
        answers = response.choices[0].message.content.split(sep='|')
        if (problemType == 5):
            answers = {"content": answers[0], "pics": [{"pic": "", "thumb": ""}]}

    return answers    
            