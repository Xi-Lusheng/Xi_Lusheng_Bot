from nonebot import get_driver, logger
import nonebot

Bot_NICKNAME: str = list(nonebot.get_driver().config.nickname)[0]

config = get_driver().config.dict()

if 'sauce_key' not in config.keys():
    logger.warning('[初号姬] 未发现配置项 `SAUCE_KEY` , 请在env中配置')
else:
    api_key = config.get('sauce_key')

if 'num_res' not in config.keys():
    logger.warning('[初号姬] 未发现配置项 `NUM_RES` , 将采用默认值：5')
    num_res = config.get('num_res', 5)
else:
    num_res = config.get('num_res')
