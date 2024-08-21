import time
from dotenv import load_dotenv
load_dotenv()
from typing import Iterator
from api import get_characterglm_response
import itertools
from data_types import TextMsg
def output_stream_response(response_stream: Iterator[str]):
    content = ""
    for content in itertools.accumulate(response_stream):
        pass
    return content


'''
实现 role-play 对话数据生成工具，要求包含下列功能：

基于一段文本（自己找一段文本，复制到提示词就可以了，比如你可以从小说中选取一部分文本，注意文本要用 markdown 格式）生成角色人设，可借助 ChatGLM 实现。
给定两个角色的人设，调用 CharacterGLM 交替生成他们的回复。
将生成的对话数据保存到文件中。
（可选）设计图形界面，通过点击图形界面上的按钮执行对话数据生成，并展示对话数据。
'''

#基于一段文本生成角色人设
# #设置两个角色的名字和人设
#测试用例1 出自《红楼梦》
# character_A_name = "贾宝玉"
# character_A_info = "荣国府衔玉而诞的公子，绰号“混世魔王”，贾政与王夫人之次子。他作为荣国府的嫡派子孙，出身不凡，聪明灵秀。他走上了叛逆之路，痛恨八股文，批判程朱理学。他终日与家里的女孩们厮混，爱她们美丽纯洁"
# character_B_name = "林黛玉"
# character_B_info = "林如海与贾敏之女，宝玉的姑表妹，寄居荣国府。她生性孤傲，不善处世，不屑种种流行的为人处事之道，多愁善感，才思敏捷。她与宝玉真心相爱,是自由恋爱的坚定追求者。"

#测试用例2 出自鲁迅雄小说《故乡》
character_A_name = "讯哥儿"
character_A_info = "讯哥儿是一个具有批判精神和反思能力的觉醒者。讯哥儿是一个对未来充满希望和期待的人。讯哥儿是一个身处城市，却对故乡怀有深深眷恋的知识分子。尽管讯哥儿对城市的繁华生活有所体验，但内心深处，却始终无法忘记那个充满童年记忆和乡土气息的故乡。"

character_B_name = "少年闰土"
character_B_info = "少年闰土是一个活泼可爱的孩子，富有表现力的少年。他的生命是有活力的，他的思想是自由的，他的心地也是善良的。跳动着的是一个活泼的生命。少年闰土较之少年的讯哥儿更富于表现力，是一个有更多的新鲜生活和新鲜感受要表达的少年。少年的“我”的知识是从书本当中获得的，少年闰土的知识则是从大自然中，从自己的生活实感中获得的。他生活在大自然中，生活在自己的生活中，他比少年讯哥儿更像一个语言艺术家。 "


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

#开始词，用于开始一段对话。
start_message = "让我们开始对话吧"
#由角色A或B以"让我们开始对话吧" 开始这段对话。Is_talK_start_from_A 为True从角色A开始
Is_talK_start_from_A = True
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