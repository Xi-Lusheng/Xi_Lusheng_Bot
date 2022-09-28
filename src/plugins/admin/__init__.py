import re

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from utils.config import Bot_NICKNAME, Bot_ID, COMMAND_START, Bot_MASTER
from utils.permission import admin_permission, get_group_role
from nonebot.plugin import PluginMetadata
from utils.utils_def import GetRe, judgment_role

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
    get_re = GetRe(event.raw_message)
    msg_id = (get_re.get_msg_id()).group(1)
    at_id_group = get_re.get_at_id()
    if msg_id and at_id_group:
        for at_id in at_id_group:
            i = 1
            id_ = at_id.group(i)
            await judgment_role(
                function=await bot.delete_msg(message_id=msg_id),
                at_id=id_,
                bot=bot,
                event=event,
                admin_func=False,
                member_func=True,
                superusers=False
            )
            i += 1
    else:
        await withdraw.finish('命令不规范，请先使用回复选择需要撤回的消息')


taboo_all = on_regex(f'^{COMMAND_START}(全体禁言|关闭全体禁言)$', priority=5, block=True)


@taboo_all.handle()
async def taboo_all_(bot: Bot, event: GroupMessageEvent):
    if await admin_permission(bot, event):
        enable = None
        if event.get_plaintext() == f'{COMMAND_START}全体禁言':
            enable = True
        elif event.get_plaintext() == f'{COMMAND_START}关闭全体禁言':
            enable = False
        await bot.set_group_whole_ban(group_id=int(event.group_id), enable=bool(enable))
    else:
        await taboo_all.finish('你没有权限使用这个命令哦', at_sender=True)


taboo = on_regex(
    r'^\s*禁言\s*(\[CQ:at,qq=[1-9][0-9]{4,10}\]\s*)+cd\d*$|^\s*(\[CQ:at,qq=[1-9][0-9]{4,10}\]\s*)+禁言\s*cd\s*\d*$',
    priority=5, block=True)


@taboo.handle()
async def taboo_(bot: Bot, event: GroupMessageEvent):
    if await admin_permission(bot, event):
        get_re = GetRe(event.raw_message)
        cd = (get_re.get_cd()).group(1)
        at_id_group = get_re.get_at_id()
        if at_id_group and cd:
            for at_id in at_id_group:
                i = 1
                id_ = at_id.group(i)
                await judgment_role(
                    function=await bot.set_group_ban(group_id=event.group_id, user_id=id_, duration=cd),
                    at_id=id_,
                    bot=bot,
                    event=event,
                    admin_func=False,
                    member_func=False,
                    superusers=False
                )
                i += 1
    else:
        await taboo.finish('你没有权限使用这个命令哦', at_sender=True)


set_admin = on_regex(r'^(设置|取消)管理员\s*\[CQ:at,qq=[1-9][0-9]{4,10}\]$|^\[CQ:at,qq=[1-9][0-9]{4,10}\]\s*(设置|取消)管理员$',
                     block=True, priority=5)


@set_admin.handle()
async def set_admin_(bot: Bot, event: GroupMessageEvent):
    if await admin_permission(bot, event):
        get_re = GetRe(event.raw_message)
        at_id = (get_re.get_at_id()).group(1)
        msg = (re.search('(设置|取消)管理员', event.raw_message)).group(1)
        if at_id and msg:
            pass
    else:
        await set_admin.finish('你没有权限使用这个命令哦', at_sender=True)
