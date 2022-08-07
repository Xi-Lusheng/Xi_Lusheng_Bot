from nonebot.plugin.on import on_message, on_notice, on_regex, on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    PokeNotifyEvent,
)
from .utils import *

ai = on_message(rule=to_me(), priority=99, block=False)

poke_ = on_notice(rule=to_me(), block=False)


@ai.handle()
async def _(event: MessageEvent):
    # 获取消息文本
    msg = str(event.get_message())
    # 去掉带中括号的内容(去除cq码)
    msg = re.sub(r"\[.*?\]", "", msg)
    # 如果是光艾特bot(没消息返回)或者打招呼的话,就回复以下内容
    if (not msg) or msg.isspace() or msg in [
        "你好啊",
        "你好",
        "在吗",
        "在不在",
        "您好",
        "您好啊",
        "嗨",
        "在",
    ]:
        await ai.finish(Message(random.choice(hello__reply)))
    # 获取用户nickname
    if isinstance(event, GroupMessageEvent):
        nickname = event.sender.card or event.sender.nickname
    else:
        nickname = event.sender.nickname
    # 从字典里获取结果
    result = await get_chat_result(msg, nickname)
    # 如果词库没有结果，则调用思知获取智能回复
    if result is None:
        message = await get_n(str(msg))
        await ai.finish(message=message)
    await ai.finish(Message(result))


@poke_.handle()
async def _poke_event(event: PokeNotifyEvent):
    if event.is_tome:
        await poke_.send(message=f"{random.choice(poke__reply)}")


xun = on_regex('^寻$', priority=5, block=True)


@xun.handle()
async def xun():
    await xun.send('寻是艾斯比')


jia_ran = on_regex('(嘉然|然然|嘉心糖)', priority=5, block=True)


@jia_ran.handle()
async def ran():
    await jia_ran.send(Message(random.choice(ran_pi)))


d2 = on_regex('命运2', priority=5, block=True)


@d2.handle()
async def d():
    await d2.send(Message('狗都不玩'))


yuan_shen = on_regex('原神', priority=5, block=True)


@yuan_shen.handle()
async def yuan():
    await yuan_shen.send(Message('卧槽！有原批'))


day = on_regex('小日向', priority=5, block=True)


@day.handle()
async def day_():
    await day.send(Message('你是不是想找别的女人了QAQ'))


wu = on_regex('呜{1,4}', priority=5, block=True)


@wu.handle()
async def wu_():
    await wu.send(Message(random.choice(wu_wu)))


_2d = on_command('二次元浓度', priority=5, block=True)


@_2d.handle()
async def _2d_():
    if random.random() < 0.7:
        try:
            await day.send(Message(str(random.randint(0, 100)) + '%'))
        except:
            await day.send(Message(random.choice(potency)))
    else:
        await day.send(Message(random.choice(potency)))

