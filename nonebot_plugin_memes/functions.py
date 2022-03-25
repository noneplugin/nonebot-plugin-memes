import imageio
from enum import Enum
from io import BytesIO
from fontTools.ttLib import TTFont
from typing import List, Tuple, Union
from typing_extensions import Literal
from PIL.Image import Image as IMG
from PIL.ImageFont import FreeTypeFont
from PIL import Image, ImageFont, ImageDraw
from emoji.unicode_codes import UNICODE_EMOJI

from .download import get_image, get_font, get_thumb


OVER_LENGTH_MSG = "文字长度过长，请适当缩减"
BREAK_LINE_MSG = "文字长度过长，请手动换行或适当缩减"
DEFAULT_FONT = "SourceHanSansSC-Regular.otf"
EMOJI_FONT = "NotoColorEmoji.ttf"


def save_jpg(frame: IMG) -> BytesIO:
    output = BytesIO()
    frame = frame.convert("RGB")
    frame.save(output, format="jpeg")
    return output


def save_png(frame: IMG) -> BytesIO:
    output = BytesIO()
    frame = frame.convert("RGBA")
    frame.save(output, format="png")
    return output


def save_gif(frames: List[IMG], duration: float) -> BytesIO:
    output = BytesIO()
    imageio.mimsave(output, frames, format="gif", duration=duration)
    return output


async def load_image(name: str) -> IMG:
    image = await get_image(name)
    return Image.open(BytesIO(image))


async def load_font(name: str, fontsize: int) -> FreeTypeFont:
    font = await get_font(name)
    return ImageFont.truetype(BytesIO(font), fontsize, encoding="utf-8")


async def load_thumb(name: str) -> IMG:
    image = await get_thumb(name)
    return Image.open(BytesIO(image))


def wrap_text(
    text: str, font: FreeTypeFont, max_width: float, stroke_width: int = 0
) -> List[str]:
    line = ""
    lines = []
    for t in text:
        if t == "\n":
            lines.append(line)
            line = ""
        elif font.getsize(line + t, stroke_width=stroke_width)[0] > max_width:
            lines.append(line)
            line = t
        else:
            line += t
    lines.append(line)
    return lines


async def fit_font_size(
    text: str,
    max_width: float,
    max_height: float,
    fontname: str,
    max_fontsize: int,
    min_fontsize: int,
    stroke_ratio: float = 0,
) -> int:
    fontsize = max_fontsize
    while True:
        font = await load_font(fontname, fontsize)
        width, height = font.getsize_multiline(
            text, stroke_width=int(fontsize * stroke_ratio)
        )
        if width > max_width or height > max_height:
            fontsize -= 1
        else:
            return fontsize
        if fontsize < min_fontsize:
            return 0


async def draw_text(
    img: IMG,
    pos: Tuple[float, float],
    text: str,
    font: FreeTypeFont,
    fill=None,
    spacing: int = 4,
    align: Literal["left", "right", "center"] = "left",
    stroke_width: int = 0,
    stroke_fill=None,
):
    if not text:
        return
    lines = text.strip().split("\n")
    draw = ImageDraw.Draw(img)
    max_w = font.getsize_multiline(text, spacing=spacing, stroke_width=stroke_width)[0]
    current_x, current_y = pos

    emoji_font_file = BytesIO(await get_font(EMOJI_FONT))
    emoji_font = ImageFont.truetype(emoji_font_file, 109, encoding="utf-8")
    emoji_ttf = TTFont(emoji_font_file)

    def has_emoji(emoji: str):
        for table in emoji_ttf["cmap"].tables:  # type: ignore
            if ord(emoji) in table.cmap.keys():
                return True
        return False

    for line in lines:
        line_w = font.getsize(line, stroke_width=stroke_width)[0]
        dw = max_w - line_w
        current_x = pos[0]
        if align == "center":
            current_x += dw / 2
        elif align == "right":
            current_x += dw

        for char in line:
            if char in UNICODE_EMOJI["en"] and has_emoji(char):
                emoji_img = Image.new("RGBA", (150, 150))
                emoji_draw = ImageDraw.Draw(emoji_img)
                emoji_draw.text((0, 0), char, font=emoji_font, embedded_color=True)
                emoji_img = emoji_img.crop(emoji_font.getbbox(char))
                emoji_x, emoji_y = font.getsize(char, stroke_width=stroke_width)
                emoji_img = fit_size(
                    emoji_img, (emoji_x, emoji_y), FitSizeMode.INSIDE, FitSizeDir.SOUTH
                )
                img.paste(emoji_img, (int(current_x), int(current_y)), emoji_img)
                current_x += emoji_x
            else:
                draw.text(
                    (current_x, current_y),
                    char,
                    font=font,
                    fill=fill,
                    stroke_width=stroke_width,
                    stroke_fill=stroke_fill,
                )
                current_x += font.getsize(char, stroke_width=stroke_width)[0]
        current_y += font.getsize("A", stroke_width=stroke_width)[1] + spacing


# 适应大小模式
class FitSizeMode(Enum):
    INSIDE = 0  # 图片必须在指定的大小范围内
    INCLUDE = 1  # 图片必须包括指定的大小范围


# 适应大小方向
class FitSizeDir(Enum):
    CENTER = 0  # 居中
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4
    NORTHWEST = 5
    NORTHEAST = 6
    SOUTHWEST = 7
    SOUTHEAST = 8


def limit_size(
    img: IMG, size: Tuple[int, int], mode: FitSizeMode = FitSizeMode.INCLUDE
) -> IMG:
    """
    调整图片到指定的大小，不改变长宽比（即返回的图片大小不一定是指定的size）
    :params
      * ``img``: 待调整的图片
      * ``size``: 期望图片大小
      * ``mode``: FitSizeMode.INSIDE 表示图片必须在指定的大小范围内；FitSizeMode.INCLUDE 表示图片必须包括指定的大小范围
    """
    w, h = size
    img_w, img_h = img.size
    if mode == FitSizeMode.INSIDE:
        ratio = min(w / img_w, h / img_h)
    elif mode == FitSizeMode.INCLUDE:
        ratio = max(w / img_w, h / img_h)
    img_w = int(img_w * ratio)
    img_h = int(img_h * ratio)
    return img.resize((img_w, img_h), Image.ANTIALIAS)


def cut_size(
    img: IMG,
    size: Tuple[int, int],
    direction: FitSizeDir = FitSizeDir.CENTER,
    bg_color: Union[str, float, Tuple[float, ...]] = (255, 255, 255, 0),
) -> IMG:
    """
    裁剪图片到指定的大小，超出部分裁剪，不足部分设为指定颜色
    :params
      * ``img``: 待调整的图片
      * ``size``: 期望图片大小
      * ``direction``: 调整图片大小时图片的方位；默认为居中 FitSizeDir.CENTER
      * ``bg_color``: FitSizeMode.INSIDE 时的背景颜色
    """
    w, h = size
    img_w, img_h = img.size
    x = int((w - img_w) / 2)
    y = int((h - img_h) / 2)
    if direction in [FitSizeDir.NORTH, FitSizeDir.NORTHWEST, FitSizeDir.NORTHEAST]:
        y = 0
    elif direction in [FitSizeDir.SOUTH, FitSizeDir.SOUTHWEST, FitSizeDir.SOUTHEAST]:
        y = h - img_h
    if direction in [FitSizeDir.WEST, FitSizeDir.NORTHWEST, FitSizeDir.SOUTHWEST]:
        x = 0
    elif direction in [FitSizeDir.EAST, FitSizeDir.NORTHEAST, FitSizeDir.SOUTHEAST]:
        x = w - img_w
    result = Image.new("RGBA", size, bg_color)
    result.paste(img, (x, y))
    return result


def fit_size(
    img: IMG,
    size: Tuple[int, int],
    mode: FitSizeMode = FitSizeMode.INCLUDE,
    direction: FitSizeDir = FitSizeDir.CENTER,
    bg_color: Union[str, float, Tuple[float, ...]] = (255, 255, 255, 0),
) -> IMG:
    """
    调整图片到指定的大小，超出部分裁剪，不足部分设为指定颜色
    :params
      * ``img``: 待调整的图片
      * ``size``: 期望图片大小
      * ``mode``: FitSizeMode.INSIDE 表示图片必须在指定的大小范围内，不足部分设为指定颜色；FitSizeMode.INCLUDE 表示图片必须包括指定的大小范围，超出部分裁剪
      * ``direction``: 调整图片大小时图片的方位；默认为居中 FitSizeDir.CENTER
      * ``bg_color``: FitSizeMode.INSIDE 时的背景颜色
    """
    return cut_size(limit_size(img, size, mode), size, direction, bg_color)
