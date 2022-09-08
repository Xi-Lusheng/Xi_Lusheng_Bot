import time
from nonebot.adapters.onebot.v11 import Message, MessageSegment, Bot, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText
from nonebot.plugin.on import on_command
from utils.config import over_list, Bot_NICKNAME
from utils.utils_def import send_forward_msg_group
from .constant import get_sakura
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='樱花',
    description='爬取樱花链接，直达播放界面',
    usage='/',
    extra={
        'menu_data': [
            {
                'func': '在樱花搜番',
                'trigger_method': 'on_cmd',
                'trigger_condition': '/樱花 或 /动漫',
                'brief_des': '输入想看的番剧，返回番剧播放链接',
                'detail_des': '输入想看的番剧，返回番剧播放链接'
            },
        ],
        'menu_template': 'default'
    }
)

sakura = on_command('动漫', aliases={'樱花'}, priority=5, block=True)


@sakura.handle()
async def sakura_(matcher: Matcher, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg:
        matcher.set_arg('name', args)


@sakura.got('name', prompt='你想看什么番呢？')
async def get_sakura_comic(bot: Bot, event: MessageEvent, name: str = ArgPlainText('name')):
    results = (await get_sakura(str(name)))[:over_list]
    await sakura.send("开始查找.....请不要进行其它操作")
    msg = []
    for result in results:
        msg.append(MessageSegment.text(result['name']) + '\n' +
                   MessageSegment.image(result['img']) + '\n' +
                   MessageSegment.text(result['url']))
    try:
        if msg:
            await send_forward_msg_group(bot,
                                         event,
                                         name=f"{Bot_NICKNAME}",
                                         msgs=msg)
        else:
            time.sleep(1)
            await sakura.send('第一次查找失败，将进行模糊查找')
            results = (await get_sakura(str(name[:2])))[:over_list]
            msg = []
            for result in results:
                msg.append(MessageSegment.text(result['name']) + '\n' +
                           MessageSegment.image(result['img']) + '\n' +
                           MessageSegment.text(result['url']))
            await send_forward_msg_group(
                bot,
                event,
                name=f"{Bot_NICKNAME}",
                msgs=msg if msg else ["没有在樱花找到这个动漫呢，换词姿势搜索试试"])
    except:
        await sakura.send('找樱花件错误，请尽快联系汐鹿生修复')
