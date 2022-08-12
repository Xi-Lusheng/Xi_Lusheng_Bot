from nonebot import get_driver, logger

config = get_driver().config.dict()

if 'sizhi_id' not in config.keys():
    logger.warning('[初号姬] 未发现配置项 `SIZHI_ID` , 请在env中配置')

else:
    app_id = config.get('sizhi_id')

if 'sizhi_user_id' not in config.keys():
    logger.warning('[初号姬] 未发现配置项 `SIZHI_USER_ID` , 请在env中配置')

else:
    user_id = config.get('sizhi_user_id')
