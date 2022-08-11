import json
import requests
import nonebot

Bot_NICKNAME: str = list(nonebot.get_driver().config.nickname)[0]

tu = [
    f'图呢？让{Bot_NICKNAME}去找空气吗？',
    '虚空识番？来图来图GKD',
    f'你把图先给{Bot_NICKNAME},不然{Bot_NICKNAME}拿头给你找啊',
    '来一份涩图，谢谢。。。。唔，不对！不许涩涩！'
]


async def get_search_pictures(image: str):
    try:
        url = 'https://saucenao.com/search.php'
        data = {
            'url': image,
            'db': '999',
            'api_key': '330a16afed184b739d4f1e2ce4dc13b8e055a53f',
            'output_type': 2,
            'numres': 4
        }

        resp = requests.get(url, params=data)

        result = json.loads(resp.content)

        json_data = result['results']
        data = []
        for i in json_data:
            similarity = i['header']['similarity']
            imgs = i['header']['thumbnail']
            if 'ext_urls' in i['data'].keys():
                from_ = (i['data']['ext_urls'][0])
            else:
                from_ = '没有找到相关链接哦'
            dic = {
                'image': imgs,
                'similarity': similarity,
                'url': from_
            }
            data.append(dic)
        return data
    except KeyError:
        return '快把图给我交了！'
