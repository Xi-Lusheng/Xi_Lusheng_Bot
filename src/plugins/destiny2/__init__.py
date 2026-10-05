import asyncio

from nonebot import logger, on_regex
from nonebot.adapters import MessageSegment
from nonebot.exception import FinishedException
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='d2',
    description='命运2日报（需要可选依赖 playwright）',
    usage='日报',
    extra={
        'menu_data': [
            {
                'func': '日报',
                'trigger_method': 'on_re',
                'trigger_condition': '日报',
                'brief_des': '查看d2日报',
                'detail_des': '需要安装 playwright 及 chromium 后才可用'
            },
        ],
        'menu_template': 'default'
    }
)

today = on_regex("^日报$", priority=5, block=True)


@today.handle()
async def today_():
    # playwright 是可选依赖，缺失时给出明确提示而不是抛 NameError
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        await today.finish(
            "「日报」功能不可用：当前环境未安装 playwright。\n"
            "如需启用：pip install playwright && playwright install chromium"
        )
        return

    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(args=["--start-maximized"])
            # 创建页面实例
            context = await browser.new_context(no_viewport=True)
            page = await context.new_page()
            # 导航到指定的URL
            await page.goto("https://data.tianque.top/today")
            await asyncio.sleep(3)
            # 截图并保存为文件
            screenshot_bytes = await page.screenshot(type="png", full_page=True)
            await context.close()
            await browser.close()
            await today.finish(MessageSegment.image(screenshot_bytes))
    # finish基于FinishedException结束事件，所以需要忽略此异常
    except FinishedException:
        raise
    except Exception as e:
        logger.opt(exception=e).warning("获取 destiny2 日报失败")
        await today.finish(f"获取日报失败: {str(e)}")
