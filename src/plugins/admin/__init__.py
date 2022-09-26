from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
import re
from utils.config import Bot_NICKNAME, Bot_ID, COMMAND_START
from utils.permission import admin_permission, get_group_role
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='管理员插件',
    description='使用命令完成管理员功能',
    usage='/',
    extra={
        'menu_data': [
            {
                'func': '撤回消息',
                'trigger_method': 'on_re',
                'trigger_condition': '[回复选择需要撤回的信息] /撤回',
                'brief_des': '撤回消息',
                'detail_des': '撤回消息'
            },
            {
                'func': '全体禁言',
                'trigger_method': 'on_re',
                'trigger_condition': '/全体禁言 /关闭全体禁言',
                'brief_des': '打开或者关闭全体禁言',
                'detail_des': '打开或者关闭全体禁言'
            },
            {
                'func': '单人禁言',
                'trigger_method': 'on_re',
                'trigger_condition': '禁言@他 cd 或 @他 禁言cd',
                'brief_des': '@要禁言的 QQ 号，cd是禁言时间，0为解除禁言',
                'detail_des': '@要禁言的 QQ 号，cd是禁言时间，0为解除禁言'
            },
        ],
        'menu_template': 'default'
    }
)
withdraw = on_regex(f"({COMMAND_START}撤回)", priority=5, block=True)


@withdraw.handle()
async def withdraw_(bot: Bot, event: GroupMessageEvent):
    r = re.search(r"\[CQ:reply,id=(-?\d*)]", str(event.raw_message))
    at = re.search(r"\[CQ:at,qq=(\d*)]", str(event.raw_message))
    if r and at:
        user_role = await get_group_role(bot, event, at.group(1))
        bot_role = await get_group_role(bot, event, Bot_ID)
        if bot_role == 'owner':
            await bot.delete_msg(message_id=int(r.group(1)))
            await withdraw.finish('已撤回')
        elif bot_role == 'admin':
            if user_role == bot_role and at.group(1) != Bot_ID or user_role == 'owner':
                await withdraw.finish(f'{Bot_NICKNAME}没有足够的权限撤回ta的消息哦')
            else:
                await bot.delete_msg(message_id=int(r.group(1)))
                await withdraw.finish('已撤回')
        else:
            await withdraw.finish(f'{Bot_NICKNAME}没有足够权限哦，让群主大大给{Bot_NICKNAME}个管理员权限吧')
    else:
        await withdraw.finish('命令不规范，请先使用回复选择需要撤回的消息')

taboo_all = on_regex(f'(^{COMMAND_START}全体禁言$|^{COMMAND_START}关闭全体禁言$)', priority=5, block=True)


@taboo_all.handle()
async def taboo_all_(bot: Bot, event: GroupMessageEvent):
    if await admin_permission(bot, event):
        enable = None
        if event.get_plaintext() == '/全体禁言':
            enable = True
        elif event.get_plaintext() == '/关闭全体禁言':
            enable = False
        await bot.set_group_whole_ban(group_id=int(event.group_id), enable=bool(enable))
    else:
        await taboo_all.finish('你没有权限使用这个命令哦', at_sender=True)


taboo = on_regex(r'^禁言\s*\[CQ:at,qq=[1-9][0-9]{4,10}\]\s*cd\d*$|^\[CQ:at,qq=[1-9][0-9]{4,10}\]\s*禁言\s*cd\d*$',
                 priority=5, block=True)


@taboo.handle()
async def taboo_(bot: Bot, event: GroupMessageEvent):
    if await admin_permission(bot, event):
        at = re.search(r"\[CQ:at,qq=(\d*)]", str(event.raw_message))
        cd = re.search(r"cd(\d*)", str(event.raw_message))
        if at and cd:
            user_role = await get_group_role(bot, event, at.group(1))
            bot_role = await get_group_role(bot, event, Bot_ID)
            if bot_role == 'owner':
                await bot.set_group_ban(group_id=event.group_id, user_id=at.group(1), duration=cd.group(1))
            elif bot_role == 'admin':
                if user_role == bot_role and at.group(1) != Bot_ID or user_role == 'owner':
                    await taboo.finish(f'{Bot_NICKNAME}没有足够的权限禁言ta哦')
                elif at.group(1) == Bot_ID:
                    await taboo.finish('你是猪比吗，你见过谁能自己禁言自己', at_sender=True)
                else:
                    await bot.set_group_ban(group_id=event.group_id, user_id=at.group(1), duration=cd.group(1))
            else:
                await taboo.finish(f'{Bot_NICKNAME}没有足够权限哦，让群主大大给{Bot_NICKNAME}个管理员权限吧')
    else:
        await taboo.finish('你没有权限使用这个命令哦', at_sender=True)

