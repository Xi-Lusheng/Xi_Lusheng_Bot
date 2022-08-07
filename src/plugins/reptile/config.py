from nonebot import get_driver, logger

config = get_driver().config.dict()

if 'overlist' not in config.keys():
    logger.warning('[初号姬] 未发现配置项 `OVERLIST` , 采用默认值: 20')
    repeater_group = config.get('overlist', 20)
else:
    repeater_group = config.get('overlist')

