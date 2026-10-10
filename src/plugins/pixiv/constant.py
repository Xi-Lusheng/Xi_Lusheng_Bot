"""幻影坦克（Mirage Tank）图片合成。

算法来自 https://github.com/Aloxaf/MirageTankGo/blob/master/MTCore/MTCore.py

【原理一句话】
    把一张图拆成两层——白底上看是"人畜无害"的图（w_img），
    黑底上看才是真图（b_img）——再按 alpha 公式逐像素混合，
    输出一张 RGBA PNG。在纯白/纯黑背景下会显示不同内容。

【本文件的职责】
    只做像素运算：缩放 -> 调亮度 -> 调色彩保留比例 -> 合成 -> 编码成 PNG。
    不联网、不碰 QQ 消息。
"""

from __future__ import annotations

import io
import os
from functools import lru_cache
from io import BytesIO
from pathlib import Path

import httpx
import numpy as np
from nonebot import logger
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

from utils.net import aget

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 输入图统一缩放到约 1000000 像素（≈1000×1000）
# 峰值内存与像素数成正比：原 4840000 像素时单张 float32 幻影坦克要 350~450MB，
# 2026-10-10 服务器（1735MB 内存）被 5 张并发请求打爆而死机，这里降到约 1/4.84。
TARGET_PIXELS = 1000000
# 白底层尺寸；会被放大到与输入图一致
CARD_SIZE = 850
# 白底上的提示字
CARD_TEXT = "你就冲吧你"
CARD_FONT_SIZE = 120

# Pillow 10 起移除了 Image.ANTIALIAS / Image.NEAREST 等顶层重采样常量
LANCZOS = Image.Resampling.LANCZOS
NEAREST = Image.Resampling.NEAREST

# 避免 0 除等运算在 numpy 2.x 下刷屏
np.seterr(divide="ignore", invalid="ignore")

_F32 = np.float32
_MAX = _F32(255.0)
_EPS = _F32(1e-6)

# 亮度权重（RGB 三通道 -> 灰度）。提到模块级只建一次，
# 不必每次合成都重新构造小数组。
_LUMA_RGB = np.array([0.334, 0.333, 0.333], dtype=np.float32)
# 最终 alpha 通道的权重（BT.601 亮度系数）
_LUMA_ALPHA = np.array([0.222, 0.707, 0.071], dtype=np.float32)

# 字体候选：优先中文字体，避免裸文件名 'simhei.ttf' 在部分环境下找不到
_FONT_CANDIDATES = (
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simsun.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
)


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------

@lru_cache(maxsize=8)
def _load_font(size: int):
    """按候选列表加载字体，全部失败时退回 Pillow 内置字体。

    【效果】加了 lru_cache：原来每合成一张图就要重新磁盘读一次字体文件
    （ttf 解析不便宜），现在同一个字号整个进程只读一次。
    """

    for candidate in _FONT_CANDIDATES:
        if os.path.exists(candidate):
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                continue

    try:
        return ImageFont.truetype("simhei.ttf", size=size)
    except OSError:
        return ImageFont.load_default()


def _lerp_toward_gray(pix: np.ndarray, color_ratio: float) -> None:
    """把 (H, W, 3) 的 RGB 数组按 color_ratio 在原色与灰度之间插值（原地修改）。

    【效果】color_ratio=1.0 完全保留原色；=0.0 完全灰度。
    对应原实现里的 w_color / b_color（色彩保留比例）。

    【为什么重写】
    原实现是
        gray = r*0.334 + g*0.333 + b*0.333
        pix *= ratio
        pix[:, :, 0] += gray * (1 - ratio)   # 再写两行 r/g/b
    对同一块 (H, W, 3) 大数组一共遍历了 4 遍。
    现在 gray 用一次矩阵乘法算出，再一次性广播加回去，大数组只遍历 2 遍。
    """

    if color_ratio >= 1.0:
        return

    gray = (pix @ _LUMA_RGB)[:, :, None]
    pix *= _F32(color_ratio)
    pix += gray * _F32(1.0 - color_ratio)


# ---------------------------------------------------------------------------
# 缩放
# ---------------------------------------------------------------------------

def resize_image(img_out: Image.Image, img_in: Image.Image, mode: str):
    """把 img_out 缩放到 img_in 的尺寸，两者都转成指定色彩模式后返回。

    【为什么这里能比原来快】
    原实现在转换之后，又把两张图各自 paste 到一张
    max(width) × max(height) 的纯色画布上居中。但：

        _w_img = img_out.convert(mode).resize(_b_img.size, NEAREST)

    _w_img 的尺寸本来就是被 _b_img.size 决定的，两张图尺寸必然一致，
    于是 width == w_width、height == b_height、paste 偏移量恒为 (0, 0)。

    那两次 Image.new + paste 纯属白干：2200×2200 的 RGB 图，
    每次要多分配约 14MB 并整图拷贝一遍，共两次。
    这里直接返回，结果是逐像素等价的。
    """

    b_img = img_in.convert(mode)
    w_img = img_out.convert(mode).resize(b_img.size, NEAREST)
    return w_img, b_img


def get_resize_image(file) -> Image.Image:
    """把下载到的原图缩放到约 4840000 像素（≈2200×2200）并转成 RGBA。

    【效果】给后续浮点运算的规模设上上限。用户图可能有 8000×8000，
    不先裁一刀的话，后面每张浮点数组就要几个 GB，10 张直接把服务器打爆。
    """

    image = Image.open(file)
    width, height = image.size

    if width * height != TARGET_PIXELS:
        ratio = (TARGET_PIXELS / (width * height)) ** 0.5
        width = int(round(width * ratio))
        height = int(round(height * ratio))
        image = image.resize((width, height), LANCZOS)

    return image.convert("RGBA")


# ---------------------------------------------------------------------------
# 合成
# ---------------------------------------------------------------------------

def get_new_image(word: str = CARD_TEXT, font_size: int = CARD_FONT_SIZE) -> Image.Image:
    """生成一张 850×850 的白色底图，中间写一行灰色提示字。

    【效果】幻影坦克的"白底"层：在白背景下看到的就是这张平平无奇的图。
    """

    new_img = Image.new("RGBA", (CARD_SIZE, CARD_SIZE), (255, 255, 255))
    draw = ImageDraw.Draw(new_img)
    width, height = new_img.size
    font = _load_font(font_size)

    # 原实现用 len(word) * font_size 估算文字宽度，只对等宽的中文大致成立，
    # 混英文数字就会偏左。draw.textlength 按字体真实度量返回宽度。
    text_width = draw.textlength(word, font=font)
    draw.text(
        xy=((width - text_width) / 2, (height - font_size) / 2),
        text=word,
        fill=(120, 120, 120),
        font=font,
    )
    return new_img


def color_car(
        w_img: Image.Image,
        b_img: Image.Image,
        w_light: float = 1.0,
        b_light: float = 0.18,
        w_color: float = 0.5,
        b_color: float = 0.7,
        chess: bool = False,
) -> BytesIO:
    """把白底层与黑底层合成为一张"彩色幻影坦克"PNG。

    :param w_img: 白背景下要显示的图
    :param b_img: 黑背景下要显示的图（真正的涩图）
    :param w_light: 白底层的亮度系数
    :param b_light: 黑底层的亮度系数
    :param w_color: 白底层的色彩保留比例（1=原色，0=灰度）
    :param b_color: 黑底层的色彩保留比例
    :param chess: 是否棋盘格化（增强对白/黑背景的锐利度）
    :return: PNG 数据的 BytesIO，可直接丢给 MessageSegment.image

    【本函数做的三种优化】
    1. float64 -> float32。2200×2200×3 的 float64 数组单个约 116MB，
       这个函数同时会有 6~8 个这样的中间数组。float32 让内存和逐元素运算都减半，
       而最终产物是 8bit PNG，float32 的 7 位有效数字完全够用。
    2. 逐通道下标运算 -> 广播运算（见 _lerp_toward_gray 与下面的 d_gray）。
    3. 少一次全图拷贝：直接组装 RGBA 输出数组，
       并用 np.clip 代替 colors[colors > 255] = 255（后者要先建一个全图布尔掩码）。
    """

    # 1) 亮度调整交给 PIL（C 实现，比在 numpy 里做快）
    w_img = ImageEnhance.Brightness(w_img).enhance(w_light)
    b_img = ImageEnhance.Brightness(b_img).enhance(b_light)

    # 2) 统一尺寸与通道
    w_img, b_img = resize_image(w_img, b_img, "RGB")

    # 3) 转 float32 并归一化到 [0, 1]
    #    np.array(..., dtype=...) 一次完成"拷贝 + 类型转换"，
    #    比原来的 np.array(img).astype("float64") 少申请一块 uint8 中间数组。
    w_pix = np.array(w_img, dtype=np.float32)
    b_pix = np.array(b_img, dtype=np.float32)
    w_pix /= _MAX
    b_pix /= _MAX

    if chess:
        w_pix[::2, ::2] = _F32(1.0)
        b_pix[1::2, 1::2] = _F32(0.0)

    # 4) 色彩保留：在原色与灰度之间插值
    _lerp_toward_gray(w_pix, w_color)
    _lerp_toward_gray(b_pix, b_color)

    # 5) 核心公式：alpha 的来源
    #    d = 1 - 白底图素 + 黑底图素，取值范围恒 >= 0
    d = 1.0 - w_pix + b_pix

    # 6) 三通道的 d 数值完全相同，因此只算一次灰度即可。
    #    原实现是把结果写回 d 的三个通道（多两遍全图拷贝）+ 另外取样求 alpha。
    d_gray = (d @ _LUMA_ALPHA)[:, :, None]

    # 7) 前景色：d 太小时直接给白色（避免除零放大成噪点）
    safe_d = np.where(np.abs(d_gray) > _EPS, d_gray, _F32(1.0))
    p = np.where(np.abs(d_gray) > _EPS, b_pix / safe_d * _MAX, _MAX)

    # 8) 组装 RGBA 输出（alpha = d * 255，clip 到 [0, 255]）
    height, width = d_gray.shape[:2]
    rgba = np.empty((height, width, 4), dtype=np.float32)
    rgba[:, :, :3] = p
    rgba[:, :, 3:] = d_gray * _MAX
    np.clip(rgba, 0.0, 255.0, out=rgba)

    output = io.BytesIO()
    # 4 通道 uint8 数组经 fromarray 得到的就是 RGBA 模式，
    # 原实现后面还跟了一句 .convert("RGBA")，那是空操作，已去掉。
    Image.fromarray(rgba.astype(np.uint8)).save(output, format="PNG")
    output.seek(0)
    return output


def make_new_image(image: bytes | BytesIO | Path) -> BytesIO:
    """把一张图做成幻影坦克，返回 PNG 的 BytesIO。

    【相对原实现的两处变化】
    1. 去掉"传 URL 字符串自己去下载"的分支。全项目没有任何调用点传字符串，
       而为了它必须把本函数写成 async，连带 resize/合成全部 async 化；
       需要联网请调用方自己下载好再传 bytes。
    2. 改成同步函数。它没有任何 await，是纯 CPU 的 numpy/PIL 运算，
       调用方用 asyncio.to_thread(make_new_image, raw) 丢到线程池里跑，
       就不会把 bot 的事件循环卡死（合成一张 2200×2200 要几百毫秒）。
    """

    if isinstance(image, bytes):
        img_in = get_resize_image(io.BytesIO(image))
    elif isinstance(image, (BytesIO, Path)):
        img_in = get_resize_image(image)
    else:
        raise ValueError(
            "make_new_image 只接受 bytes / BytesIO / Path；"
            "网络图片请先下载成 bytes 再传入"
        )

    img_on = get_new_image()
    return color_car(img_on, img_in)


# ---------------------------------------------------------------------------
# 下载
# ---------------------------------------------------------------------------

async def func(client: httpx.AsyncClient, urls: str) -> bytes | None:
    """下载一张图片。成功返回 bytes，失败返回 None（不抛异常）。

    【效果】一张图下载失败不应该影响其它图，也不该让整条命令报错，
    所以这里把异常全部吃掉并记一条 warning，由调用方过滤掉 None。
    下载同样会偶发 DNS 解析失败，用带重试的 aget 兜底。
    """

    try:
        resp = await aget(client, urls)
    except Exception as exc:
        logger.warning(f"[pixiv] 下载图片失败：{urls} -> {type(exc).__name__}: {exc}")
        return None

    if resp.status_code != 200:
        logger.warning(f"[pixiv] 下载图片失败：{urls} -> HTTP {resp.status_code}")
        return None

    return resp.content
