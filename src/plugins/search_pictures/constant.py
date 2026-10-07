import requests
from utils.config import sauce_key, num_res, pictures_number

# saucenao_api 是可选依赖：它会把 requests/urllib3 降级到远古版本，
# 因此不进 requirements.txt。这里做软导入，保证没装它时插件本体仍能加载，
# 只有 /识图 真正被调用时才提示缺少依赖。
try:
    from saucenao_api import SauceNao
except ImportError:  # pragma: no cover - 取决于部署环境
    SauceNao = None

_SAUCENAO_HINT = "缺少可选依赖 saucenao-api，/识图 功能暂不可用（pip install saucenao-api）"


async def get_search_pictures(image: str) -> list[dict[str]]:
    if SauceNao is None:
        raise RuntimeError(_SAUCENAO_HINT)

    sauce = SauceNao(sauce_key, numres=num_res)
    results = sauce.from_url(image)
    data = []
    for i in range(len(results)):
        result = results[i]
        if result.similarity > 50:
            dic = {
                'image': result.thumbnail,
                'author': result.author,
                'similarity': str(result.similarity),
                'url': ''.join(result.urls)
            }
            data.append(dic)
    return data


async def get_anime(image: str) -> list[dict[str]] or str:
    url = "https://api.trace.moe/search?anilistInfo&url={}".format(image)
    anime_json = (requests.get(url)).json()
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
            dic = {
                'anime_name': anime_name,
                'episode': str(anime["episode"]),
                'similarity': '{:.2%}'.format(anime["similarity"]),
                'image': anime["image"]
            }
            data.append(dic)
        return data
    else:
        return '发生了奇怪的错误，再试一次？'
