from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Bot, Message
from nonebot.internal.params import Arg
from nonebot.params import CommandArg
from nonebot.plugin.on import on_command
from nonebot.typing import T_State
from utils.config import Bot_NICKNAME
from utils.utils_def import send_forward_msg_group, get_message_img
from .constant import get_search_pictures, get_anime

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
        await picture.reject_arg('img_url', '发送的必须是图片！')
    img_url = img_url[0]
    try:
        data = await get_search_pictures(img_url)
        await picture.send('开始识别.....请不要进行其它操作')
        if data is None:
            await picture.send(f'没有找到相似的图片，果咩..', at_sender=True)
        else:
            msg = []
            for datas in data:
                msg.append(Message('对比图片' +
                                   '\n' +
                                   MessageSegment.image(datas['image']) +
                                   '\n' +
                                   '相似度：{} '.format(
                                       MessageSegment.text(datas['similarity'])) +
                                   '\n' +
                                   '图片来源' +
                                   '\n' +
                                   MessageSegment.text(datas['url'])))
            try:
                await send_forward_msg_group(bot, event, name='初号姬', msgs=msg if msg else ['没有找到相似的图片呢，换一张试试'])
            except:
                await picture.send('搜图插件出现错误，请尽快练习联系汐鹿生修复')
    except TypeError or KeyError:
        await picture.send(f'{Bot_NICKNAME}今天找图找累了，明天再来吧')
    except:
        await anime.send('搜图插件出现错误，请尽快练习联系汐鹿生修复')


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
                await send_forward_msg_group(bot, event, name='初号姬', msgs=msg if msg else ['没有找到相似的图片呢，换一张试试'])
            except:
                await anime.send('搜图插件出现错误，请尽快练习联系汐鹿生修复')
    except TypeError or KeyError:
        await anime.send(f'{Bot_NICKNAME}这个月找番找累了，下个月再来吧')
    except:
        await anime.send('搜图插件出现错误，请尽快练习联系汐鹿生修复')
