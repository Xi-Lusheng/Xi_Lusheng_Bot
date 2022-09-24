from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.permission import SUPERUSER
import re
from utils.config import Bot_NICKNAME, Bot_ID, COMMAND_START

withdraw = on_regex(f"({COMMAND_START}撤回)", priority=5, block=True, permission=SUPERUSER)


@withdraw.handle()
async def withdraw_(bot: Bot, event: GroupMessageEvent):
    r = re.search(r"\[CQ:reply,id=(-?\d*)]", event.raw_message)
    at = re.search(r"\[CQ:at,qq=(\d*)]", event.raw_message)
    if r and at:
        group_id = event.group_id
        print(group_id)
        print(at.group(1))
        user_role = (await bot.get_group_member_info(
            group_id=group_id,
            user_id=int(at.group(1)),
            no_cache=False))['role']
        bot_role = (await bot.get_group_member_info(
            group_id=group_id,
            user_id=Bot_ID,
            no_cache=False))['role']
        if bot_role == 'owner':
            await bot.delete_msg(message_id=int(r.group(1)))
        elif bot_role == 'admin':
            if user_role == bot_role and at.group(1) != Bot_ID or user_role == 'owner':
                await withdraw.finish(f'{Bot_NICKNAME}没有足够的权限撤回ta的消息哦')
            else:
                await bot.delete_msg(message_id=int(r.group(1)))
        else:
            await withdraw.finish(f'{Bot_NICKNAME}没有足够权限哦，让群主大大给{Bot_NICKNAME}个管理员权限吧')


# taboo_all = on_regex(f'(^{COMMAND_START}全体禁言$|^{COMMAND_START}关闭全体禁言$)', priority=5, block=True, permission=SUPERUSER)
#
#
# @taboo_all.handle()
# async def taboo_all_(bot: Bot, event: GroupMessageEvent):
#     group_id = event.group_id
#     bot_role = (await bot.get_group_member_info(
#         group_id=group_id,
#         user_id=Bot_ID,
#         no_cache=False))['role']
#
#     await bot.set_group_whole_ban(group_id=int(event.group_id), enable=bool(True))

