"""涩图插件的持久化配置：data/setu/customer_api.json。

文件结构（键是群号或 QQ 号，值是该会话的偏好）：

    {
        "295104399": {"url": "lolicon API", "r18": false},
        "428733650": {"url": "lolicon API", "r18": true}
    }

【本模块实现的效果】
    把"读配置 / 写配置 / 取某个群的配置"三件事收口到一处，
    handler 里不再出现 customer_api 的字典操作和落盘代码。
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from nonebot import logger

# 配置目录与文件名（原实现是 Path() / "data" / "setu"，效果相同）
DATA_DIR = Path("data") / "setu"
CONFIG_FILE = DATA_DIR / "customer_api.json"

# 一个会话（群或私聊）的偏好；缺字段时由 get_session() 补上
SessionConfig = dict[str, Any]
CustomerApi = dict[str, SessionConfig]

DEFAULT_SESSION: SessionConfig = {
    "url": "lolicon API",
    "r18": False,
}


def load() -> CustomerApi:
    """读取配置文件，返回 {会话id: 偏好}。

    【效果】整个进程只在 import 时读一次盘。
    文件不存在（首次运行）或内容损坏（半个 JSON）时返回空字典并记一条 warning，
    绝不因为一个坏文件让插件加载失败——原实现在 json.load 抛异常时会直接炸掉 import。
    """

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning(f"[pixiv] 配置文件 {CONFIG_FILE} 读取失败，已按空配置处理：{exc}")
        return {}

    return data if isinstance(data, dict) else {}


def save(data: CustomerApi) -> None:
    """把配置写回磁盘（原子写）。

    【为什么不用原来的写法】
    原实现是 with open(file, "w") 直接覆写目标文件。如果写到一半进程被 kill
    （比如 systemd 重启、我们手动 restart），customer_api.json 就只剩半截，
    下次启动再也读不回来，用户的 r18 开关全部丢失。

    【现在的效果】
    先在同目录写一个临时文件，再用 os.replace 覆盖。os.replace 在同一个文件系统内
    是原子操作：任何时刻读这个路径，要么是完整旧版本，要么是完整新版本。
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=DATA_DIR, prefix=".customer_api-", suffix=".tmp")

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, CONFIG_FILE)
    except BaseException:
        # 写失败就把临时文件删掉，别在 data/setu 里堆垃圾
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def get_session(session_id: str) -> SessionConfig:
    """取出（必要时新建）某个群/用户的偏好字典，返回值可直接修改。

    【效果】原来这两段代码在"发涩图"和"开关 r18"两个 handler 里各写了一遍：

        if id_ not in customer_api.keys():
            customer_api[f"{id_}"] = {}
        api = customer_api[f"{id_}"].get("url", "lolicon API")

    现在收敛成一次 get_session(id)，且返回的字典一定带齐默认字段，
    调用方不用再到处写 .get(..., 默认值)。
    """

    session = customer_api.get(session_id)

    if not isinstance(session, dict):
        session = dict(DEFAULT_SESSION)
        customer_api[session_id] = session
        return session

    # 老配置文件里可能只有一半字段，这里补齐
    for key, value in DEFAULT_SESSION.items():
        session.setdefault(key, value)

    return session


def set_r18(session_id: str, enabled: bool) -> SessionConfig:
    """修改某个会话的 r18 开关并立即落盘。

    【效果】调用方只需要 set_r18("295104399", True)，
    不用再记住"改完要调 save()"。
    """

    session = get_session(session_id)
    session["r18"] = enabled
    save(customer_api)
    return session


# 进程级缓存：import 时读一次，之后所有 handler 共用这一份
customer_api: CustomerApi = load()
