from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent


async def admin_permission(bot: Bot, event: GroupMessageEvent) -> bool:
    """
    判断是否用户是管理员，群主或者开发者权限

    :param bot: bot对象
    :param event: 群消息
    :return: boolean
    """
    user_role = (await bot.get_group_member_info(
        group_id=event.group_id,
        user_id=int(event.get_user_id()),
        no_cache=False))['role']
    if user_role == 'owner' or user_role == 'admin' or event.get_user_id() in bot.config.superusers:
        return True


async def get_group_role(bot: Bot, event: GroupMessageEvent, user_id: str) -> str:
    """
    输出对象在群组中的权限

    :param user_id: 对象id
    :param bot: bot对象
    :param event: 群消息
    :return: 群权限
    """
    role = (await bot.get_group_member_info(
        group_id=event.group_id,
        user_id=user_id,
        no_cache=False
    ))['role']
    return role


