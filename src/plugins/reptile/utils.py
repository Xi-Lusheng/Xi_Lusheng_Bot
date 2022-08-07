import requests
from bs4 import BeautifulSoup
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent


async def get_sakura(text):
    try:
        url = f'https://www.yhdmw.com/comicsearch/-------------.html?wd={text}&submit='
        util_url = 'https://www.yhdmw.com/'
        resp = requests.get(url)
        main_page = BeautifulSoup(resp.text, 'html.parser')
        src = main_page.find_all('a', attrs={
            'class': 'myui-vodlist__thumb img-lg-150 img-md-150 img-sm-150 img-xs-100 lazyload'
        })
        data = []
        for i in src:
            href = util_url + i.get('href').strip('/')
            title = i.get('title')
            img = util_url + i.get('data-original').strip('/')
            dic = {
                'name': title,
                'url': href,
                'img': img
            }
            data.append(dic)
        return data
    except TypeError:
        return '快点告诉我你想看什么！'


# 消息合并转发
async def send_forward_msg_group(
        bot: Bot,
        event: MessageEvent,
        name: str,
        msgs: [],
):
    def to_json(msg):
        return {"type": "node", "data": {"name": name, "uin": bot.self_id, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    if isinstance(event, GroupMessageEvent):
        await bot.call_api(
            "send_group_forward_msg", group_id=event.group_id, messages=messages
        )
    else:
        await bot.call_api(
            "send_private_forward_msg", user_id=event.user_id, messages=messages
        )

