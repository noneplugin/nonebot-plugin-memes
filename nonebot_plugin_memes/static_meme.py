from io import BytesIO
from datetime import datetime
from typing import List, Union
from PIL import Image, ImageDraw

from .functions import load_image, load_font, save_jpg, save_png, \
    wrap_text, fit_font_size, DEFAULT_FONT, OVER_LENGTH_MSG, BREAK_LINE_MSG


async def make_luxunsay(texts: List[str]) -> Union[str, BytesIO]:
    font = await load_font(DEFAULT_FONT, 38)
    luxun_font = await load_font(DEFAULT_FONT, 30)
    lines = wrap_text(texts[0], font, 430)
    if len(lines) > 2:
        return OVER_LENGTH_MSG
    text = '\n'.join(lines)
    spacing = 5
    text_w, text_h = font.getsize_multiline(text, spacing=spacing)
    frame = await load_image('luxunsay.jpg')
    x = 240 - text_w / 2
    y = 350 - text_h / 2
    draw = ImageDraw.Draw(frame)
    draw.multiline_text((x, y), text, font=font,
                        align='center', spacing=spacing, fill=(255, 255, 255))
    draw.text((320, 400), '--鲁迅', font=luxun_font, fill=(255, 255, 255))
    return save_png(frame)


async def make_nokia(texts: List[str]) -> Union[str, BytesIO]:
    font = await load_font('方正像素14.ttf', 70)
    lines = wrap_text(texts[0][:900], font, 700)[:5]
    text = '\n'.join(lines)
    angle = -9.3

    img_text = Image.new('RGBA', (700, 450))
    draw = ImageDraw.Draw(img_text)
    draw.multiline_text((0, 0), text, font=font,
                        spacing=30, fill=(0, 0, 0, 255))
    img_text = img_text.rotate(angle, expand=True)

    head = f'{len(text)}/900'
    img_head = Image.new('RGBA', font.getsize(head))
    draw = ImageDraw.Draw(img_head)
    draw.text((0, 0), head, font=font, fill=(129, 212, 250, 255))
    img_head = img_head.rotate(angle, expand=True)

    frame = await load_image('nokia.jpg')
    frame.paste(img_text, (205, 330), mask=img_text)
    frame.paste(img_head, (790, 320), mask=img_head)
    return save_jpg(frame)


async def make_goodnews(texts: List[str]) -> Union[str, BytesIO]:
    text = texts[0]
    fontsize = await fit_font_size(text, 460, 280, DEFAULT_FONT, 80, 25, 1/15)
    if not fontsize:
        return BREAK_LINE_MSG
    font = await load_font(DEFAULT_FONT, fontsize)
    stroke_width = fontsize // 15
    text_w, text_h = font.getsize_multiline(text, stroke_width=stroke_width)

    frame = await load_image('goodnews.jpg')
    draw = ImageDraw.Draw(frame)
    img_w, img_h = frame.size
    x = (img_w - text_w) / 2
    y = (img_h - text_h) / 2
    draw.multiline_text((x, y), text, font=font, fill=(238, 0, 0), align="center",
                        stroke_width=stroke_width, stroke_fill=(255, 255, 153))
    return save_png(frame)


async def make_jichou(texts: List[str]) -> Union[str, BytesIO]:
    date = datetime.today().strftime('%Y{}%m{}%d{}').format('年', '月', '日')
    text = f"{date} 晴\n{texts[0]}\n这个仇我先记下了"
    font = await load_font(DEFAULT_FONT, 45)
    lines = wrap_text(text, font, 440)
    if len(lines) > 10:
        return OVER_LENGTH_MSG
    text = '\n'.join(lines)
    spacing = 10
    _, text_h = font.getsize_multiline(text, spacing=spacing)
    frame = await load_image('jichou.png')
    img_w, img_h = frame.size
    bg = Image.new('RGB', (img_w, img_h + text_h + 20), (255, 255, 255))
    bg.paste(frame, (0, 0))
    draw = ImageDraw.Draw(bg)
    draw.multiline_text((30, img_h + 5), text, font=font,
                        spacing=spacing, fill=(0, 0, 0))
    return save_jpg(bg)


async def make_fanatic(texts: List[str]) -> Union[str, BytesIO]:
    text = texts[0]
    fontsize = await fit_font_size(text, 190, 100, DEFAULT_FONT, 70, 30)
    if not fontsize:
        return BREAK_LINE_MSG
    font = await load_font(DEFAULT_FONT, fontsize)
    text_w, text_h = font.getsize_multiline(text)

    frame = await load_image('fanatic.jpg')
    x = 242 - text_w / 2
    y = 90 - text_h / 2
    draw = ImageDraw.Draw(frame)
    draw.multiline_text((x, y), text, align='center',
                        font=font, fill=(0, 0, 0))
    return save_jpg(frame)


async def make_diyu(texts: List[str]) -> Union[str, BytesIO]:
    text = texts[0]
    fontsize = await fit_font_size(text, 420, 56, DEFAULT_FONT, 40, 20)
    if not fontsize:
        return OVER_LENGTH_MSG
    font = await load_font(DEFAULT_FONT, fontsize)
    text_w, text_h = font.getsize_multiline(text)

    frame = await load_image('diyu.png')
    draw = ImageDraw.Draw(frame)
    x = 220 - text_w / 2
    y = 272 - text_h / 2
    draw.text((x, y), text, font=font, fill='#000000', align='center')
    return save_png(frame)


static_memes = {
    'luxunsay': {
        'aliases': {'鲁迅说', '鲁迅说过'},
        'func': make_luxunsay
    },
    'nokia': {
        'aliases': {'诺基亚', '有内鬼'},
        'func': make_nokia
    },
    'goodnews': {
        'aliases': {'喜报'},
        'func': make_goodnews
    },
    'jichou': {
        'aliases': {'记仇'},
        'func': make_jichou
    },
    'fanatic': {
        'aliases': {'狂爱', '狂粉'},
        'func': make_fanatic
    },
    'diyu': {
        'aliases': {'低语'},
        'func': make_diyu
    }
}
