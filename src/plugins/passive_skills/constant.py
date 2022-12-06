import requests


async def get_image(sort: int) -> str:
    url = 'https://api.xilusheng.top/nonebot/pixiv/random/'
    data = requests.get(url, params={"sort": sort}).json()
    image = data['data'][0]['image']
    return image
