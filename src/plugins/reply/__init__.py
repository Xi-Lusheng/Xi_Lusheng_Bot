from nonebot.plugin.on import on_message, on_notice, on_regex
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    GroupMessageEvent,
    Message,
    MessageEvent,
    PokeNotifyEvent,
    MessageSegment
)
from .utils import *

xun = on_regex('^寻$', priority=5, block=True)


@xun.handle()
async def xun(bot: Bot, event: Event):
    if int(event.get_user_id()) != event.self_id:
        str1 = '寻是艾斯比'
        await bot.send(event=event, message=str1)


# 优先级99, 条件: 艾特bot就触发
ai = on_message(rule=to_me(), priority=99, block=False)
# 优先级1, 不会向下阻断, 条件: 戳一戳bot触发
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
