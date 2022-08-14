import json
import requests
from utils.config import sauce_key, num_res, pictures_number


async def get_search_pictures(image: str):
    try:
        url = 'https://saucenao.com/search.php'
        data = {
            'url': image,
            'db': '999',
            'api_key': sauce_key,
            'output_type': 2,
            'numres': num_res,
        }

        resp = requests.get(url, params=data)

        result = json.loads(resp.content)

        data = []
        for i in result['results']:
            similarity = i['header']['similarity']
            image = i['header']['thumbnail']
            if 'ext_urls' in i['data'].keys():
                from_ = (i['data']['ext_urls'][0])
            else:
                from_ = '没有找到相关链接哦'
            dic = {
                'image': image,
                'similarity': similarity,
                'url': from_
            }
            data.append(dic)
        return data
    except KeyError:
        return '快把图给我交了！'


async def get_anime(image):
    url = "https://api.trace.moe/search?anilistInfo&url={}".format(image)
    anime_json = (requests.get(url)).json()
    try:
        if not anime_json["error"]:
            if anime_json == "Error reading imagenull":
                return None
            data = []
            # 拿到动漫 中文名
            for anime in anime_json["result"][:pictures_number]:
                synonyms = anime["anilist"]["synonyms"]
                for x in synonyms:
                    _count_ch = 0
                    for word in x:
                        if "\u4e00" <= word <= "\u9fff":
                            _count_ch += 1
                    if _count_ch > 3:
                        anime_name = x
                        break
                else:
                    anime_name = anime["anilist"]["title"]["native"]
                episode = str(anime["episode"])
                similarity = '{:.2%}'.format(anime["similarity"])
                image = anime["image"]
                dic = {
                    'anime_name': anime_name,
                    'episode': episode,
                    'similarity': similarity,
                    'image': image
                }
                data.append(dic)
            return data
        else:
            return None
    except:
        return "发生了奇怪的错误，那就没办法了，再试一次？"
