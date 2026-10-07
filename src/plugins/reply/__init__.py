import random
from nonebot.internal.matcher import Matcher
from nonebot.plugin.on import on_message, on_notice, on_regex, on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageEvent,
    PokeNotifyEvent,
)
from src.plugins.reply.constant import get_chat_result, utils_get_chat_result
import re
from data.reply_data.msg_data import *
from nonebot.plugin import PluginMetadata
from utils.config import COMMAND_START

__plugin_meta__ = PluginMetadata(
    name='AI聊天',
    description='人工智能（智障）聊天',
    usage='@我 聊天内容',
)


poke_ = on_notice(rule=to_me(), block=False)


@poke_.handle()
async def _poke_event(event: PokeNotifyEvent):
    if event.is_tome:
        await poke_.send(message=f"{random.choice(poke__reply)}")


# 触发被动词
util_msg = on_message(priority=99, block=True)


@util_msg.handle()
async def util_msg_(event: MessageEvent):
    if random.randint(0, 10) <= 7:
        msg = str(event.get_message())
        if msg[0] == f'{COMMAND_START}':
            pass
        else:
            msg = re.sub(r"\[.*?\]", "", msg)
            result = await utils_get_chat_result(msg)
            if result:
                await util_msg.finish(Message(result))


_2d = on_command('二次元浓度', priority=5, block=True)


@_2d.handle()
async def _2d_():
    if random.randint(0, 10) > 7:
        await _2d.send(Message(str(random.randint(0, 100)) + '%'))
    else:
        await _2d.send(Message(random.choice(potency)))


# 低概率复读
repeat = on_message(priority=97, block=False)


@repeat.handle()
async def repeat_(matcher: Matcher, event: MessageEvent):
    if random.randint(0, 500) == 500:
        msg = str(event.get_message())
        matcher.stop_propagation()
        await repeat.send(Message(msg))


wu = on_regex('^呜{1,4}$', priority=5, block=True)


@wu.handle()
async def wu_():
    await wu.send(Message(random.choice(wu_wu)))
