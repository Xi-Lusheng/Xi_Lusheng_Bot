from nonebot.plugin import PluginMetadata
from utils.config import Bot_NICKNAME

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
        ],
        'menu_template': 'default'
    }
)

