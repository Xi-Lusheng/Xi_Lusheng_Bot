import requests


async def get_image() -> str:
    url = 'https://api.xilusheng.top/nonebot/pixiv/random/'
    data = requests.get(url).json()
    image = data['data'][0]['image']
    return image
