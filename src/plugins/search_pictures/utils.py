import json
import time
import requests
from utils.config import sauce_key, num_res


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

# def get_anime(name):
#     s_time = time.time()
#     url = "https://api.trace.moe/search?anilistInfo&url={}".format(name)
#     anime_json = (requests.get(url)).json()
#     try:
#         if not anime_json["error"]:
#             if anime_json == "Error reading imagenull":
#                 return "图像源错误，注意必须是静态图片哦"
#             repass = ""
#             # 拿到动漫 中文名
#             for anime in anime_json["result"][:5]:
#                 synonyms = anime["anilist"]["synonyms"]
#                 for x in synonyms:
#                     _count_ch = 0
#                     for word in x:
#                         if "\u4e00" <= word <= "\u9fff":
#                             _count_ch += 1
#                     if _count_ch > 3:
#                         anime_name = x
#                         break
#                 else:
#                     anime_name = anime["anilist"]["title"]["native"]
#                 episode = anime["episode"]
#                 from_ = int(anime["from"])
#                 m, s = divmod(from_, 60)
#                 similarity = anime["similarity"]
#                 putline = "[ {} ][{}][{}:{}] 相似度:{:.2%}".format(
#                     Converter("zh-hans").convert(anime_name),
#                     episode if episode else "?",
#                     m,
#                     s,
#                     similarity,
#                 )
#                 repass += putline + "\n"
#             return f"耗时 {int(time.time() - s_time)} 秒\n" + repass[:-1]
#         else:
#             return f'访问错误 error：{anime_json["error"]}'
#     except Exception as e:
#         return "发生了奇怪的错误，那就没办法了，再试一次？"
#
#
# get_anime(
#     'https://gchat.qpic.cn/gchatpic_new/428733650/4185104399-2881036140-AD55C6830BAAAE87B6E8C8C5CF40052D/0?term=3]')
