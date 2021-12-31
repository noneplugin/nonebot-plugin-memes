from io import BytesIO
from PIL import ImageDraw
from typing import List, Tuple, Union


from .functions import load_image, load_font, save_gif, DEFAULT_FONT, OVER_LENGTH_MSG


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
        text_w, text_h = font.getsize(text, stroke_width=1)
        if text_w > img_w - padding_x * 2:
            return OVER_LENGTH_MSG
        x = int((img_w - text_w) / 2)
        y = img_h - text_h - padding_y
        for frame in part:
            draw = ImageDraw.Draw(frame)
            draw.text((x, y), text, font=font, fill=(255, 255, 255),
                      stroke_width=1, stroke_fill=(0, 0, 0))
    return save_gif(frames, img.info['duration'] / 1000)


gif_memes = {
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


for key, config in gif_memes.copy().items():
    gif_memes[key]['func'] = gif_func(config)
    gif_memes[key]['arg_num'] = len(config['pieces'])
