from nonebot.adapters.onebot.exception import ActionFailed
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Bot, Message
from nonebot.internal.params import Arg
from nonebot.params import CommandArg
from nonebot.plugin.on import on_command
from nonebot.typing import T_State
from utils.config import Bot_NICKNAME
from utils.utils_def import send_forward_msg_group, get_message_img
from .constant import get_search_pictures, get_anime
from nonebot.plugin import PluginMetadata
from requests.exceptions import ConnectionError

__plugin_meta__ = PluginMetadata(
    name='识图',
    description='查找图片的原画或者动漫出处',
    usage='/',
    extra={
        'menu_data': [
            {
                'func': '查找原画',
                'trigger_method': 'on_cmd',
                'trigger_condition': '/识图 图片',
                'brief_des': '发送图片寻找图片出处\n'
                             '（每天只能使用100次，否则会罢工）',
                'detail_des': '发送图片寻找图片出处\n'
                              '（每天只能使用100次，否则会罢工）'
            },
            {
                'func': '查找动漫',
                'trigger_method': 'on_cmd',
                'trigger_condition': '/识番 图片',
                'brief_des': '发送图片寻找番剧出处\n'
                             '（每月只能使用1000次，否则会罢工）',
                'detail_des': '发送图片寻找图片出处\n'
                              '（每月只能使用1000次，否则会罢工）'
            },
        ],
        'menu_template': 'default'
    }
)

picture = on_command('识图', priority=5, block=True)


@picture.handle()
async def _(event: MessageEvent, state: T_State, args: Message = CommandArg()):
    img_url = get_message_img(event.json())
    if img_url:
        state['img_url'] = args


@picture.got('img_url', prompt=f'图呢？让{Bot_NICKNAME}去找空气吗？')
async def _(bot: Bot, event: MessageEvent, img_url: Message = Arg('img_url')):
    img_url = get_message_img(img_url)
    if not img_url:
        await picture.reject_arg('img_url', '发送的必须是图片！', at_sender=True)
    img_url = img_url[0]
    try:
        datas = await get_search_pictures(img_url)
        await picture.send('开始识别.....请不要进行其它操作', at_sender=True)
        if datas is None:
            await picture.send(f'没有找到相似的图片，果咩..', at_sender=True)
        else:
            msgs = []
            for data in datas:
                msgs.append(Message('对比图片' + '\n' + MessageSegment.image(data['image']) + '\n' +
                                    '相似度：{} %'.format(MessageSegment.text(data['similarity'])) + '\n' +
                                    '作者:' + '\n' + MessageSegment.text(data['author']) + '\n' +
                                    '图片来源' + '\n' + MessageSegment.text(data['url'])))
            try:
                await send_forward_msg_group(bot, event, name=f'{Bot_NICKNAME}',
                                             msgs=msgs if msgs else ['没有找到相似的图片呢，换一张试试'])
            except ActionFailed:
                await picture.finish(f'{Bot_NICKNAME}可能被企鹅风控了', at_sender=True)
    except ConnectionError:
        await picture.finish(f'等一下！太快了！让{Bot_NICKNAME}休息一会吧', at_sender=True)


anime = on_command('识番', priority=5, block=True)


@anime.handle()
async def _(event: MessageEvent, state: T_State, args: Message = CommandArg()):
    img_url = get_message_img(event.json())
    if img_url:
        state['img_url'] = args


@anime.got('img_url', prompt=f'图呢？让{Bot_NICKNAME}去找空气吗？')
async def _(bot: Bot, event: MessageEvent, img_url: Message = Arg('img_url')):
    try:
        img_url = get_message_img(img_url)
        if not img_url:
            await anime.reject_arg('img_url', '发送的必须是图片！')
        img_url = img_url[0]
        data = await get_anime(img_url)
        await anime.send('开始识别.....请不要进行其它操作')
        if data is None:
            await anime.send(f'没有找到相似的图片，果咩..', at_sender=True)
        else:
            msg = []
            for datas in data:
                msg.append(Message('动漫名称: {}'.format(MessageSegment.text(datas['anime_name'])) + '\n' +
                                   MessageSegment.image(datas['image']) + '\n' +
                                   '第 {} 集'.format(MessageSegment.text(datas['episode'])) + '\n' +
                                   '相似度：{} %'.format(MessageSegment.text(datas['similarity']))))

            try:
                await send_forward_msg_group(bot, event, name=f'{Bot_NICKNAME}',
                                             msgs=msg if msg else ['没有找到相似的图片呢，换一张试试'])
            except ActionFailed:
                await picture.finish(f'{Bot_NICKNAME}可能被企鹅风控了', at_sender=True)
    except ConnectionError:
        await picture.finish(f'等一下！太快了！让{Bot_NICKNAME}休息一会吧', at_sender=True)
    except TypeError or KeyError:
        await anime.finish(f'{Bot_NICKNAME}这个月找番找累了，下个月再来吧')
    except:
        await anime.finish('插件出现未知错误，请尽快练习联系汐鹿生修复')
