from nonebot import on_notice, on_message
from nonebot.adapters.onebot.v11 import (GroupIncreaseNoticeEvent, GroupDecreaseNoticeEvent, MessageSegment,
                                         PrivateMessageEvent, Bot)
from nonebot.plugin import PluginMetadata
from utils.config import Bot_NICKNAME
from src.plugins.passive_skills.constant import get_image

__plugin_meta__ = PluginMetadata(
    name='被动技能',
    description='被动技能信息',
    usage='',
    extra={
        'menu_data': [
            {
                'func': '复读姬',
                'trigger_method': 'on_msg',
                'trigger_condition': '群消息开始+1',
                'brief_des': f'当有人开始复读时{Bot_NICKNAME}也会参一脚',
                'detail_des': f'当有人开始复读时{Bot_NICKNAME}也会参一脚'
            },
            {
                'func': '复读姬2.0',
                'trigger_method': 'on_msg',
                'trigger_condition': '随机',
                'brief_des': '低概率复读',
                'detail_des': '低概率复读'
            },
            {
                'func': '胡言乱语',
                'trigger_method': 'on_msg',
                'trigger_condition': '秘密',
                'brief_des': f'{Bot_NICKNAME}时不时会胡言乱语',
                'detail_des': f'{Bot_NICKNAME}时不时会胡言乱语'
            },
            {
                'func': '不能戳！',
                'trigger_method': 'on_notice',
                'trigger_condition': f'戳{Bot_NICKNAME}',
                'brief_des': f'不能随便戳{Bot_NICKNAME}！',
                'detail_des': f'不能随便戳{Bot_NICKNAME}！'
            },
            {
                'func': '二次元浓度',
                'trigger_method': 'on_cmd',
                'trigger_condition': '/二次元浓度',
                'brief_des': '查询二次元浓度(雾',
                'detail_des': '查询二次元浓度(雾'
            },
            {
                'func': '群成员变动通知',
                'trigger_method': 'on_notice',
                'trigger_condition': '群成员变动',
                'brief_des': '群成员变动通知',
                'detail_des': '群成员变动通知'
            },
        ],
        'menu_template': 'default'
    }
)

notice = on_notice()


@notice.handle()
async def welcome(event: GroupIncreaseNoticeEvent):
    user_id = event.get_user_id()
    welcome_image = await get_image(sort=0)
    msg = "欢迎大佬" + \
          MessageSegment.at(user_id) + '\n' + \
          MessageSegment.image(welcome_image) + '\n' + \
          '群友都是南通，说话又好听，欢迎你的加入'
    await notice.finish(msg)


@notice.handle()
async def decrease(event: GroupDecreaseNoticeEvent):
    user = event.get_user_id()
    msg = "{} 退出了群聊".format(user)
    await notice.finish(msg)


test_friend = on_message(priority=1, block=False)


@test_friend.handle()
async def friends_(bot: Bot, event: PrivateMessageEvent):
    user_id = event.get_user_id()
    friend_list = await bot.get_friend_list()
    id_list = []
    for friends in friend_list:
        friend_id = friends.get('user_id')
        id_list.append(friend_id)
    if int(user_id) in id_list:
        pass
    else:
        await test_friend.finish('机器人功能并不对陌生人开放，请私聊机器人管理员添加好友')

