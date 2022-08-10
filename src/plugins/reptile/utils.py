import requests
from bs4 import BeautifulSoup


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


