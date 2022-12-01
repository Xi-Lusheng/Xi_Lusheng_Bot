import requests
from nonebot.adapters.onebot.v11 import MessageSegment, Message
import re
import io
from typing import Tuple
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import base64


async def get_image(msg: str) -> Message:
    r18 = re.search('r18', msg)
    url = 'https://api.xilusheng.top/nonebot/pixiv/random/'
    if r18:
        params = {
            "is_r18": True
        }
        data = requests.get(url, params=params).json()
        image_r18 = data['data'][0]['image']
        image_id = data['data'][0]['id']
        image_path = requests.get(image_r18)
        img = Image.new('RGB', (350, 350), (100, 100, 100))
        draw = ImageDraw.Draw(img)
        width, height = img.size
        word = "你就冲吧你"
        font_size = 50
        font = ImageFont.truetype('simhei.ttf', size=font_size)
        w, h = len(word) * font_size, font_size
        draw.text(xy=((width - w) / 2, (height - h) / 2), text=word, fill=(120, 120, 120), font=font)
        img_on = img.copy()
        img_in = Image.open(io.BytesIO(image_path.content))
        image = await color_car(img_on, img_in)
        res = MessageSegment.image(f"base64://{base64.b64encode(image.getvalue()).decode()}")
        result = res + MessageSegment.text(f"图片id：{image_id} \n"
                                           f"原图片链接：{image_r18}")
    else:
        data = requests.get(url).json()
        image = data['data'][0]['image']
        image_id = data['data'][0]['id']
        res = MessageSegment.image(image)
        result = MessageSegment.text(f"图片id：{image_id}\n") + res
    return result


np.seterr(divide="ignore", invalid="ignore")


# ------来自 https://github.com/Aloxaf/MirageTankGo/blob/master/MTCore/MTCore.py----------------
async def resize_image(
        img_out: Image.Image, img_in: Image.Image, mode
) -> Tuple[Image.Image, Image.Image]:
    """
    统一图像大小
    """
    _b_img = img_in.convert(mode)
    _w_img = img_out.convert(mode).resize(_b_img.size, Image.NEAREST)

    w_width, w_height = _w_img.size
    b_width, b_height = _b_img.size

    width = max(w_width, b_width)
    height = max(w_height, b_height)

    w_img = Image.new(mode, (width, height), 255)
    b_img = Image.new(mode, (width, height), 0)

    w_img.paste(_w_img, ((width - w_width) // 2, (height - w_height) // 2))
    b_img.paste(_b_img, ((width - b_width) // 2, (height - b_height) // 2))

    return w_img, b_img


async def color_car(
        w_img: Image.Image,
        b_img: Image.Image,
        w_light: float = 1.0,
        b_light: float = 0.18,
        w_color: float = 0.5,
        b_color: float = 0.6,
        chess: bool = False,
):
    """
    发彩色车
    :param w_img: 白色背景下的图片
    :param b_img: 黑色背景下的图片
    :param w_light: w_img 的亮度
    :param b_light: b_img 的亮度
    :param w_color: w_img 的色彩保留比例
    :param b_color: b_img 的色彩保留比例
    :param chess: 是否棋盘格化
    :return: 处理后的图像
    """
    w_img = ImageEnhance.Brightness(w_img).enhance(w_light)
    b_img = ImageEnhance.Brightness(b_img).enhance(b_light)

    w_img, b_img = await resize_image(w_img, b_img, "RGB")

    w_pix = np.array(w_img).astype("float64")
    b_pix = np.array(b_img).astype("float64")

    if chess:
        w_pix[::2, ::2] = [255.0, 255.0, 255.0]
        b_pix[1::2, 1::2] = [0.0, 0.0, 0.0]

    w_pix /= 255.0
    b_pix /= 255.0

    w_gray = w_pix[:, :, 0] * 0.334 + w_pix[:, :, 1] * 0.333 + w_pix[:, :, 2] * 0.333
    w_pix *= w_color
    w_pix[:, :, 0] += w_gray * (1.0 - w_color)
    w_pix[:, :, 1] += w_gray * (1.0 - w_color)
    w_pix[:, :, 2] += w_gray * (1.0 - w_color)

    b_gray = b_pix[:, :, 0] * 0.334 + b_pix[:, :, 1] * 0.333 + b_pix[:, :, 2] * 0.333
    b_pix *= b_color
    b_pix[:, :, 0] += b_gray * (1.0 - b_color)
    b_pix[:, :, 1] += b_gray * (1.0 - b_color)
    b_pix[:, :, 2] += b_gray * (1.0 - b_color)

    d = 1.0 - w_pix + b_pix

    d[:, :, 0] = d[:, :, 1] = d[:, :, 2] = (
            d[:, :, 0] * 0.222 + d[:, :, 1] * 0.707 + d[:, :, 2] * 0.071
    )

    p = np.where(abs(d) > 1e-6, b_pix / d * 255.0, 255.0)
    a = d[:, :, 0] * 255.0

    colors = np.zeros((p.shape[0], p.shape[1], 4))
    colors[:, :, :3] = p
    colors[:, :, -1] = a

    colors[colors > 255] = 255

    output = io.BytesIO()
    Image.fromarray(colors.astype("uint8")).convert("RGBA").save(output, format="png")
    return output
