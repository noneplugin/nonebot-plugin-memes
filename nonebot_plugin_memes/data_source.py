import imageio
from io import BytesIO
from datetime import datetime
from PIL.Image import Image as IMG
from typing import List, Tuple, Union
from PIL.ImageFont import FreeTypeFont
from PIL import Image, ImageFont, ImageDraw

from .download import get_image, get_font


OVER_LENGTH_MSG = '文字长度过长，请适当缩减'
DEFAULT_FONT = 'msyh.ttc'


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


async def make_gif(filename: str, texts: List[str], pieces: List[Tuple[int, int]],
                   fontsize: int = 20, padding_x: int = 5, padding_y: int = 5) -> Union[str, BytesIO]:
    img = await load_image(filename)
    frames = []
    for i in range(img.n_frames):
        img.seek(i)
        frames.append(img.convert('RGB'))

    font = await load_font(DEFAULT_FONT, fontsize)
    parts = [frames[start:end] for start, end in pieces]
    img_w, img_h = frames[0].size
    for part, text in zip(parts, texts):
        text_w, text_h = font.getsize(text)
        if text_w > img_w - padding_x * 2:
            return OVER_LENGTH_MSG
        x = int((img_w - text_w) / 2)
        y = img_h - text_h - padding_y
        for frame in part:
            draw = ImageDraw.Draw(frame)
            draw.text((x, y), text, font=font, fill=(255, 255, 255),
                      stroke_width=1, stroke_fill=(0, 0, 0))
    return save_gif(frames, img.info['duration'] / 1000)


gif_configs = {
    'wangjingze': {
        'aliases': {'王境泽'},
        'filename': 'wangjingze.gif',
        'pieces': [(0, 9), (12, 24), (25, 35), (37, 48)],
        'fontsize': 20
    },
    'weisuoyuwei': {
        'aliases': {'为所欲为'},
        'filename': 'weisuoyuwei.gif',
        'pieces': [(11, 14), (27, 38), (42, 61), (63, 81), (82, 95),
                   (96, 105), (111, 131), (145, 157), (157, 167)],
        'fontsize': 19
    },
    'chanshenzi': {
        'aliases': {'馋身子', '馋她身子'},
        'filename': 'chanshenzi.gif',
        'pieces': [(0, 16), (16, 31), (33, 40)],
        'fontsize': 18
    },
    'qiegewala': {
        'aliases': {'切格瓦拉'},
        'filename': 'qiegewala.gif',
        'pieces': [(0, 15), (16, 31), (31, 38), (38, 48), (49, 68), (68, 86)],
        'fontsize': 20
    },
    'shuifandui': {
        'aliases': {'谁赞成谁反对', '谁反对'},
        'filename': 'shuifandui.gif',
        'pieces': [(3, 14), (21, 26), (31, 38), (40, 45)],
        'fontsize': 19
    },
    'zengxiaoxian': {
        'aliases': {'曾小贤', '连连看'},
        'filename': 'zengxiaoxian.gif',
        'pieces': [(3, 15), (24, 30), (30, 46), (56, 63)],
        'fontsize': 21
    },
    'yalidaye': {
        'aliases': {'压力大爷'},
        'filename': 'yalidaye.gif',
        'pieces': [(0, 16), (21, 47), (52, 77)],
        'fontsize': 21
    },
    'nihaosaoa': {
        'aliases': {'你好骚啊'},
        'filename': 'nihaosaoa.gif',
        'pieces': [(0, 14), (16, 26), (42, 61)],
        'fontsize': 17
    },
    'shishilani': {
        'aliases': {'食屎啦你'},
        'filename': 'shishilani.gif',
        'pieces': [(14, 21), (23, 36), (38, 46), (60, 66)],
        'fontsize': 17
    },
    'wunian': {
        'aliases': {'五年怎么过的', '贪玩蓝月'},
        'filename': 'wunian.gif',
        'pieces': [(11, 20), (35, 50), (59, 77), (82, 95)],
        'fontsize': 16
    }
}


def gif_func(config: dict):
    async def func(texts: List[str]) -> Union[str, BytesIO]:
        return await make_gif(config['filename'], texts, config['pieces'], config['fontsize'])
    return func


def wrap_text(text: str, font: FreeTypeFont, max_width: float) -> List[str]:
    line = ''
    lines = []
    for t in text:
        if t == '\n':
            lines.append(line)
            line = ''
        elif font.getsize(line + t)[0] > max_width:
            lines.append(line)
            line = t
        else:
            line += t
    lines.append(line)
    return lines


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
    img_w, img_h = frame.size
    x = int((img_w - text_w) / 2)
    y = int((img_h - text_h) / 2) + 110
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
    font = await load_font(DEFAULT_FONT, 45)
    lines = wrap_text(texts[0], font, 480)
    if len(lines) > 5:
        return OVER_LENGTH_MSG
    text = '\n'.join(lines)
    spacing = 8
    stroke_width = 3
    text_w, text_h = font.getsize_multiline(text, spacing=spacing,
                                            stroke_width=stroke_width)
    frame = await load_image('goodnews.jpg')
    img_w, img_h = frame.size
    x = int((img_w - text_w) / 2)
    y = int((img_h - text_h) / 2)
    draw = ImageDraw.Draw(frame)
    draw.multiline_text((x, y), text, font=font,
                        align='center', spacing=spacing, fill=(238, 0, 0),
                        stroke_width=stroke_width, stroke_fill=(255, 255, 153))
    return save_png(frame)


async def make_jichou(texts: List[str]) -> Union[str, BytesIO]:
    date = datetime.today().strftime('%Y{}%m{}%d{}').format('年', '月', '日')
    text = f"{date} 晴\n{texts[0]}\n这个仇我先记下了"
    font = await load_font(DEFAULT_FONT, 45)
    lines = wrap_text(text, font, 440)
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
    font = await load_font(DEFAULT_FONT, 36)
    lines = wrap_text(texts[0], font, 180)
    if len(lines) > 2:
        return OVER_LENGTH_MSG
    text = '\n'.join(lines)
    text_w, text_h = font.getsize_multiline(text)
    frame = await load_image('fanatic.jpg')
    x = 240 - int(text_w / 2)
    y = 90 - int(text_h / 2)
    draw = ImageDraw.Draw(frame)
    draw.multiline_text((x, y), text, align='center',
                        font=font, fill=(0, 0, 0))
    return save_jpg(frame)


memes = {
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
    }
}

for key, config in gif_configs.items():
    memes[key] = {
        'aliases': config['aliases'],
        'func': gif_func(config),
        'arg_num': len(config['pieces'])
    }


async def make_meme(type: str, texts: List[str]) -> Union[str, BytesIO]:
    return await memes[type]['func'](texts)
