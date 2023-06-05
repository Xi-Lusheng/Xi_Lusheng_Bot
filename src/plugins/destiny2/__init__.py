from nonebot import on_regex
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
from nonebot.plugin import PluginMetadata
import asyncio
from playwright.async_api import async_playwright

__plugin_meta__ = PluginMetadata(
    name='d2',
    description='暂时维护中，勿用',
    usage='',
    extra={
        'menu_data': [
            {
                'func': '日报',
                'trigger_method': 'on_re',
                'trigger_condition': '日报',
                'brief_des': '查看d2日报',
                'detail_des': '暂时维护中，勿用'
            },
        ],
        'menu_template': 'default'
    }
)

today = on_regex("^日报$", priority=5, block=True)


@today.handle()
async def today_():
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
            await today.finish(MessageSegment.image(screenshot_bytes))
            # 关闭浏览器
            await context.close()
            await browser.close()
    # finish基于FinishedException结束事件，所以需要忽略此异常
    except FinishedException:
        raise
    except Exception as e:
        print(repr(e))
        await today.finish(f"获取日报失败: {str(e)}")
