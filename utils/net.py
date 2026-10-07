"""带重试的 HTTP 请求工具。

图源域名（api.lolicon.app / i.pixiv.re / saucenao 等）在部分网络环境下会偶发
DNS 解析失败，报错形如：

    [Errno -2] Name or service not known      # Linux 服务器
    [Errno 11001] getaddrinfo failed          # Windows 本地

一次解析失败就会让整条"来N张色图"流程直接跳到最外层 except，
表现为"出现错误：…"，看起来像是合并转发坏了，其实根本没走到转发那一步。
所以在网络层做有限次重试，把偶发抖动吸收掉。
"""

import asyncio
import time

import httpx
from nonebot import logger

DEFAULT_RETRIES = 3
DEFAULT_TIMEOUT = 20.0
RETRY_BACKOFF = 0.8


def _is_retryable(exc: BaseException) -> bool:
    # httpx.ConnectError（DNS 解析失败会被包在这里）也是 httpx.HTTPError 的子类
    return isinstance(exc, (httpx.HTTPError, OSError))


def _log_retry(url: str, attempt: int, retries: int, exc: BaseException) -> None:
    logger.warning(
        f"[http] 请求 {url} 失败（第 {attempt}/{retries} 次）：{type(exc).__name__}: {exc}"
    )


def get(
    url: str,
    *,
    retries: int = DEFAULT_RETRIES,
    timeout: float = DEFAULT_TIMEOUT,
    **kwargs,
) -> httpx.Response:
    """同步 GET，遇到网络/DNS 错误自动重试，最终仍失败则抛出最后一次异常。"""
    last_exc: BaseException | None = None
    for attempt in range(1, retries + 1):
        try:
            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                return client.get(url, **kwargs)
        except Exception as exc:
            if not _is_retryable(exc):
                raise
            last_exc = exc
            _log_retry(url, attempt, retries, exc)
            if attempt < retries:
                time.sleep(RETRY_BACKOFF * attempt)
    assert last_exc is not None
    raise last_exc


async def aget(
    client: httpx.AsyncClient,
    url: str,
    *,
    retries: int = DEFAULT_RETRIES,
    **kwargs,
) -> httpx.Response:
    """在已有的 AsyncClient 上 GET，遇到网络/DNS 错误自动重试。"""
    last_exc: BaseException | None = None
    for attempt in range(1, retries + 1):
        try:
            return await client.get(url, **kwargs)
        except Exception as exc:
            if not _is_retryable(exc):
                raise
            last_exc = exc
            _log_retry(url, attempt, retries, exc)
            if attempt < retries:
                await asyncio.sleep(RETRY_BACKOFF * attempt)
    assert last_exc is not None
    raise last_exc
