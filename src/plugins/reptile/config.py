from nonebot import get_driver, logger

config = get_driver().config.dict()

if 'over_list' not in config.keys():
    logger.warning('[初号姬] 未发现配置项 `OVER_LIST` , 采用默认值: 20')
    repeater_group = config.get('over_list', 20)
else:
    repeater_group = config.get('over_list')


