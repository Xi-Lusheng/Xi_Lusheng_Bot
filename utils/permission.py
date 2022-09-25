from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent


async def admin_permission(bot: Bot, event: GroupMessageEvent) -> bool:
    user_role = (await bot.get_group_member_info(
        group_id=event.group_id,
        user_id=int(event.get_user_id()),
        no_cache=False))['role']
    if user_role == 'owner' or user_role == 'admin' or event.get_user_id() in bot.config.superusers:
        return True

