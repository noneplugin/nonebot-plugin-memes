import imageio
from io import BytesIO
from typing import List
from PIL.Image import Image as IMG
from PIL.ImageFont import FreeTypeFont
from PIL import Image, ImageFont

from .download import get_image, get_font, get_thumb


OVER_LENGTH_MSG = '文字长度过长，请适当缩减'
BREAK_LINE_MSG = '文字长度过长，请手动换行或适当缩减'
DEFAULT_FONT = 'SourceHanSansSC-Regular.otf'


def save_jpg(frame: IMG) -> BytesIO:
    output = BytesIO()
    frame = frame.convert('RGB')
    frame.save(output, format='jpeg')
    return output


def save_png(frame: IMG) -> BytesIO:
    output = BytesIO()
    frame = frame.convert('RGBA')
    frame.save(output, format='png')
    return output


def save_gif(frames: List[IMG], duration: float) -> BytesIO:
    output = BytesIO()
    imageio.mimsave(output, frames, format='gif', duration=duration)
    return output


async def load_image(name: str) -> IMG:
    image = await get_image(name)
    return Image.open(BytesIO(image))


async def load_font(name: str, fontsize: int) -> FreeTypeFont:
    font = await get_font(name)
    return ImageFont.truetype(BytesIO(font), fontsize, encoding='utf-8')


async def load_thumb(name: str) -> IMG:
    image = await get_thumb(name)
    return Image.open(BytesIO(image))


def wrap_text(text: str, font: FreeTypeFont, max_width: float, stroke_width: int = 0) -> List[str]:
    line = ''
    lines = []
    for t in text:
        if t == '\n':
            lines.append(line)
            line = ''
        elif font.getsize(line + t, stroke_width=stroke_width)[0] > max_width:
            lines.append(line)
            line = t
        else:
            line += t
    lines.append(line)
    return lines


async def fit_font_size(text: str, max_width: float, max_height: float,
                        fontname: str, max_fontsize: int, min_fontsize: int,
                        stroke_ratio: float = 0) -> int:
    fontsize = max_fontsize
    while True:
        font = await load_font(fontname, fontsize)
        width, height = font.getsize_multiline(
            text, stroke_width=int(fontsize * stroke_ratio))
        if width > max_width or height > max_height:
            fontsize -= 1
        else:
            return fontsize
        if fontsize < min_fontsize:
            return 0
