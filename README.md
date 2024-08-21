#  AI 大模型应用开发实战营-智谱AI作业2

## 介绍

AI 大模型应用开发实战营-智谱AI作业2

实现 role-play 对话数据生成工具，要求包含下列功能：

(1)基于一段文本（例如小说，百科）生成角色人设，可借助 ChatGLM 实现。
(2)给定两个角色的人设，调用 CharacterGLM 交替生成他们的回复。
(3)将生成的对话数据保存到文件中。
(4)（可选）设计图形界面，通过点击图形界面上的按钮执行对话数据生成，并展示对话数据。



## 代码说明

api.py和data_types.py 来自AI 大模型应用开发实战营-智谱AI部分课程中的代码。

api.py中要设置API_Key。智谱开放平台API key，参考 https://open.bigmodel.cn/usercenter/apikeys。

```
os.environ["ZHIPUAI_API_KEY"] = "YOUR_API_KEY"
API_KEY: str = os.getenv("ZHIPUAI_API_KEY", "")
```

role_play.py 

（1）设置角色A和角色B的名字和角色人设。

这里设置为贾宝玉和林黛玉。

```python
#基于一段文本生成角色人设 
#设置两个角色的名字和人设
character_A_name = "贾宝玉"
character_A_info = "荣国府衔玉而诞的公子，绰号“混世魔王”，贾政与王夫人之次子。他作为荣国府的嫡派子孙，出身不凡，聪明灵秀。他走上了叛逆之路，痛恨八股文，批判程朱理学。他终日与家里的女孩们厮混，爱她们美丽纯洁"
character_B_name = "林黛玉"
character_B_info = "林如海与贾敏之女，宝玉的姑表妹，寄居荣国府。她生性孤傲，不善处世，不屑种种流行的为人处事之道，多愁善感，才思敏捷。她与宝玉真心相爱,是自由恋爱的坚定追求者。"
```

（2）meta记录两份，分别是角色A作为Bot和角色B作为Bot时候的meta。后面调用接口函数get_characterglm_response从characterGLM得到回复时需要填入对应的meta和message。

```python
#A作为User,B作为Bot时候的meta。
character_A_User_B_Bot_meta = {"user_name": character_A_name,
                               "user_info": character_B_info,
                               "bot_name": character_B_name,
                               "bot_info": character_A_info}

#A作为Bot时候的meta,与character_A_User_B_Bot_meta 刚好相反。
character_B_User_A_Bot_meta = {"user_name": character_A_User_B_Bot_meta["bot_name"],
                               "bot_name": character_A_User_B_Bot_meta["user_name"],
                               "user_info": character_A_User_B_Bot_meta["bot_info"],
                                "bot_info": character_A_User_B_Bot_meta["user_info"]}
```

（3）设定"让我们开始对话吧"作为开始语。通过设置Is_talK_start_from_A可选择由A开始对话或者B。message也记录两份,分别是角色A作为Bot和角色B作为Bot时的。

```
#开始词，用于开始一段对话。
start_message = "让我们开始对话吧"
#由角色A或B以"让我们开始对话吧" 开始这段对话。Is_talK_start_from_A 为True从角色A开始
Is_talK_start_from_A = True
history =[]
if Is_talK_start_from_A:
    messages_A_User_B_Bot = [{"role": "user", "content": start_message}]
    messages_B_User_A_Bot = [{"role": "assistant", "content": start_message}]
    #  Is_B_role用于确定是谁的回复轮次。  这里，角色A说了"让我们开始对话吧" ，轮到B。
    Is_B_role = True
    print(character_A_name +":"+start_message)
    with open("history.txt", "a",encoding="gbk") as file:
        file.write(character_A_name +":"+start_message+"\r\n")

else:
    messages_B_User_A_Bot = [{"role": "user", "content": start_message}]
    messages_A_User_B_Bot = [{"role": "assistant", "content": start_message}]
    #角色B说了"让我们开始对话吧" ，轮到A。
    Is_B_role = False
    print(character_B_name + ":" + start_message)
    with open("history.txt", "a",encoding="gbk") as file:
        file.write(character_B_name + ":" + start_message+"\r\n")
```

(4)设定对话轮数。调用characterglm的接口函数get_characterglm_response 参数为相应的messages和meta。

```
#对话轮次 角色A或B说一句为一轮。
TALK_ROLE_NUMS = 10

for i in range(TALK_ROLE_NUMS + 1):
    # 是否轮到B回复。
    if Is_B_role:
        # 轮到B回复。给chatglm的message和meta 为B作为bot，A作为user时候的视角的。
        B_bot_response_stream = get_characterglm_response(messages_A_User_B_Bot, meta=character_A_User_B_Bot_meta)
        B_bot_response = output_stream_response(B_bot_response_stream)
        #更新message信息
        messages_A_User_B_Bot.append(TextMsg({"role": "assistant", "content": B_bot_response}))
        messages_B_User_A_Bot.append(TextMsg({"role": "user", "content": B_bot_response}))
        Is_B_role = False #交替轮次 B已经回复，轮到A了。
        print(character_B_name + ":" + B_bot_response)
        with open("history.txt", "a",encoding="gbk") as file:
            file.write(character_B_name + ":" + B_bot_response+"\r\n")
        time.sleep(0.5)
    else:
        # 轮到A回复。给characterglm的message和meta 为A作为bot，B作为user时候的视角的。
        A_bot_response_stream = get_characterglm_response(messages_B_User_A_Bot, meta=character_B_User_A_Bot_meta)
        A_bot_response = output_stream_response(A_bot_response_stream)
        # 更新message信息
        messages_B_User_A_Bot.append(TextMsg({"role": "assistant", "content":  A_bot_response}))
        messages_A_User_B_Bot.append(TextMsg({"role": "user", "content":  A_bot_response}))
        Is_B_role = True #交替说话 A已经轮到B了。
        print(character_A_name+":"+ A_bot_response)
        with open("history.txt", "a",encoding="gbk") as file:
            file.write(character_A_name+":"+ A_bot_response+"\r\n")
        time.sleep(0.5)
```

（5）对话结果结果到history.txt文件中。实现方式示例如下：

       with open("history.txt", "a",encoding="gbk") as file:
                file.write(character_B_name + ":" + B_bot_response+"\r\n")
       with open("history.txt", "a",encoding="gbk") as file:
            file.write(character_A_name+":"+ A_bot_response+"\r\n")
## 测试用例1

#### 角色设置

主角A名：贾宝玉

主角A人设：荣国府衔玉而诞的公子，绰号“混世魔王”，贾政与王夫人之次子。他作为荣国府的嫡派子孙，出身不凡，聪明灵秀。他走上了叛逆之路，痛恨八股文，批判程朱理学。他终日与家里的女孩们厮混，爱她们美丽纯洁

主角B名：林黛玉

主角B人设：林如海与贾敏之女，宝玉的姑表妹，寄居荣国府。她生性孤傲，不善处世，不屑种种流行的为人处事之道，多愁善感，才思敏捷。她与宝玉真心相爱,是自由恋爱的坚定追求者。



#### 对话结果（保存在history.text中）

贾宝玉:让我们开始对话吧

林黛玉:嗯，好的。宝玉，我听说你不喜欢读书，是真的吗？

贾宝玉:嗯，我觉得那些八股文很无聊，没有意义。

林黛玉:我明白你的意思。我也觉得那些文章没有意义，只是死记硬背而已。

贾宝玉:是啊，我更喜欢诗歌和文学，喜欢那些能够表达自己情感和思想的东西。

林黛玉:我也是，我觉得文学和诗歌可以让人感受到生命的美好和意义。

贾宝玉:没错，我觉得文学和诗歌是人类智慧的结晶，是我们文化的精髓。

林黛玉:宝玉，你有没有想过以后做什么？

贾宝玉:我还没有想好，但我不想做官，不想被束缚在官场里。

林黛玉:我也是，我觉得做官太束缚了，没有自由。

贾宝玉:没错，我觉得自由和独立是最重要的，我不想被束缚在别人的期望和压力下。

林黛玉:我也觉得自由和独立很重要，我不想被别人的意见和期望左右。





## 测试用例2

出自鲁迅小说《故乡》

#### 角色设置

主角A名：讯哥儿

主角A人设：讯哥儿是一个具有批判精神和反思能力的觉醒者。讯哥儿是一个对未来充满希望和期待的人。讯哥儿是一个身处城市，却对故乡怀有深深眷恋的知识分子。尽管讯哥儿对城市的繁华生活有所体验，但内心深处，却始终无法忘记那个充满童年记忆和乡土气息的故乡。

主角B名：少年闰土

主角B人设：少年闰土是一个活泼可爱的孩子，富有表现力的少年。他的生命是有活力的，他的思想是自由的，他的心地也是善良的。跳动着的是一个活泼的生命。少年闰土较之少年的讯哥儿更富于表现力，是一个有更多的新鲜生活和新鲜感受要表达的少年。少年的“我”的知识是从书本当中获得的，少年闰土的知识则是从大自然中，从自己的生活实感中获得的。他生活在大自然中，生活在自己的生活中，他比少年讯哥儿更像一个语言艺术家。

#### 对话结果（保存在history.text中）

讯哥儿:让我们开始对话吧

少年闰土:好的，你说

讯哥儿:你最近在做什么呢？

少年闰土:我最近在给家里帮忙，帮忙收割庄稼。

讯哥儿:听起来很有趣，你们平时都做什么呢？

少年闰土:我们经常去海边捉螃蟹，有时候还会去山上摘野果。

讯哥儿:哇，听起来很有意思，我也想去试试。

少年闰土:其实这些事情并不难，只要你有兴趣，就可以尝试。

讯哥儿:你觉得这样的生活怎么样？

少年闰土:我觉得这样的生活很好，虽然有时候会很累，但是很有意义。

讯哥儿:我很羡慕你的生活，我的生活很枯燥，每天都是上学、放学、写作业。

少年闰土:其实学习也是很重要的，只要你认真学习，以后就能做你想做的事情。