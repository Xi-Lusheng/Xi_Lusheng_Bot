"""自动更新结果通知。

服务器端的 scripts/auto_update.sh 在自动更新失败并回滚后，会在项目根目录写下
.update_status.json。本插件在 bot 启动后拉起一个后台任务，发现这个文件就
私聊管理员（SUPERUSERS，缺省 428733650），发送成功后删除文件。

【为什么用“写文件 + 插件读取”，而不是脚本里直接调 QQ 接口】
脚本要发消息就得去调 NapCat 的 HTTP API，而 NapCat 现在没有开 HTTP 服务，
开启它需要重启容器、会丢掉 QQ 登录态（要重新扫码）。让已经连上 QQ 的 bot
自己发消息，既不用动 NapCat，也天然能在回滚重启后立刻发出通知。
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from nonebot import get_bots, get_driver, logger
from nonebot.adapters.onebot.v11 import Message

# __file__ = <repo>/src/plugins/autoupdate/__init__.py，往上四层就是项目根目录
REPO_ROOT = Path(__file__).resolve().parents[3]
STATUS_FILE = REPO_ROOT / ".update_status.json"

# 启动后先等一会儿，避免 OneBot 的 WebSocket 还没连上就查 get_bots()
STARTUP_DELAY = 15
CHECK_INTERVAL = 30
FALLBACK_ADMIN = "428733650"

_driver = get_driver()


def _admin_list() -> list[str]:
    """取 SUPERUSERS；没配就退回默认管理员，保证通知不会因为配置缺失而发不出去。"""

    admins = getattr(_driver.config, "superusers", None)
    return sorted({str(qq) for qq in admins}) if admins else [FALLBACK_ADMIN]


async def _check_once() -> None:
    if not STATUS_FILE.exists():
        return

    bots = get_bots()
    if not bots:
        # OneBot 还没连上，留着文件下次再试
        return

    try:
        data = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        # 文件坏了就挪走，否则每 30 秒刷一次同样的报错
        logger.warning(f"[autoupdate] 更新状态文件无法解析，已重命名：{exc}")
        STATUS_FILE.replace(STATUS_FILE.with_suffix(".json.bad"))
        return

    if data.get("status") != "failed":
        STATUS_FILE.unlink(missing_ok=True)
        return

    text = f"""【自动更新失败】
时间：{data.get('time', '未知')}
原因：{data.get('message', '未知')}
详情：{data.get('detail', '无')}

已自动回滚到上一个可用版本。完整日志见服务器 /var/log/xilusheng-autoupdate.log
"""

    bot = next(iter(bots.values()))
    for qq in _admin_list():
        try:
            await bot.send_private_msg(user_id=int(qq), message=Message(text))
        except Exception:
            logger.exception(f"[autoupdate] 私聊管理员 {qq} 失败，保留标记稍后重试")
            return

    # 全部发完才删，保证至少成功通知过一次
    STATUS_FILE.unlink(missing_ok=True)
    logger.info("[autoupdate] 自动更新失败通知已发送给管理员")


async def _watch_loop() -> None:
    await asyncio.sleep(STARTUP_DELAY)
    while True:
        try:
            await _check_once()
        except Exception:
            logger.exception("[autoupdate] 检查更新失败标记时出错")
        await asyncio.sleep(CHECK_INTERVAL)


@_driver.on_startup
async def _start_watcher() -> None:
    asyncio.create_task(_watch_loop())
