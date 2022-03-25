from io import BytesIO
from functools import partial
from typing import List, Tuple, Union

from .models import NormalMeme, MultiArgMeme
from .functions import *


async def make_gif(
    texts: List[str],
    filename: str,
    pieces: Tuple[Tuple[int, int], ...],
    fontsize: int = 20,
    padding_x: int = 5,
    padding_y: int = 5,
) -> Union[str, BytesIO]:
    img = await load_image(filename)
    frames = []
    for i in range(img.n_frames):
        img.seek(i)
        frames.append(img.convert("RGB"))

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
            await draw_text(
                frame,
                (x, y),
                text,
                font=font,
                fill=(255, 255, 255),
                stroke_width=1,
                stroke_fill=(0, 0, 0),
            )
    return save_gif(frames, img.info["duration"] / 1000)


def gif_func(filename: str, pieces: Tuple[Tuple[int, int], ...], **kwargs):
    return partial(make_gif, filename=filename, pieces=pieces, **kwargs)


gif_subtitle_memes: List[NormalMeme] = [
    MultiArgMeme(
        ("王境泽",),
        "wangjingze.jpg",
        gif_func("wangjingze.gif", ((0, 9), (12, 24), (25, 35), (37, 48))),
        ("我就是饿死", "死外边 从这里跳下去", "不会吃你们一点东西", "真香"),
    ),
    # fmt: off
    MultiArgMeme(
        ("为所欲为",),
        "weisuoyuwei.jpg",
        gif_func("weisuoyuwei.gif", ((11, 14), (27, 38), (42, 61), (63, 81), (82, 95), (96, 105), (111, 131), (145, 157), (157, 167)), fontsize=19),
        ("好啊", "就算你是一流工程师", "就算你出报告再完美", "我叫你改报告你就要改", "毕竟我是客户", "客户了不起啊", "Sorry 客户真的了不起", "以后叫他天天改报告", "天天改 天天改"),
    ),
    # fmt: on
    MultiArgMeme(
        ("馋身子",),
        "chanshenzi.jpg",
        gif_func("chanshenzi.gif", ((0, 16), (16, 31), (33, 40)), fontsize=18),
        ("你那叫喜欢吗？", "你那是馋她身子", "你下贱！"),
    ),
    MultiArgMeme(
        ("切格瓦拉",),
        "qiegewala.jpg",
        gif_func(
            "qiegewala.gif", ((0, 15), (16, 31), (31, 38), (38, 48), (49, 68), (68, 86))
        ),
        ("没有钱啊 肯定要做的啊", "不做的话没有钱用", "那你不会去打工啊", "有手有脚的", "打工是不可能打工的", "这辈子不可能打工的"),
    ),
    MultiArgMeme(
        ("谁反对",),
        "shuifandui.jpg",
        gif_func(
            "shuifandui.gif", ((3, 14), (21, 26), (31, 38), (40, 45)), fontsize=19
        ),
        ("我话说完了", "谁赞成", "谁反对", "我反对"),
    ),
    MultiArgMeme(
        ("曾小贤", "连连看"),
        "zengxiaoxian.jpg",
        gif_func(
            "zengxiaoxian.gif", ((3, 15), (24, 30), (30, 46), (56, 63)), fontsize=21
        ),
        ("平时你打电子游戏吗", "偶尔", "星际还是魔兽", "连连看"),
    ),
    MultiArgMeme(
        ("压力大爷",),
        "yalidaye.jpg",
        gif_func("yalidaye.gif", ((0, 16), (21, 47), (52, 77)), fontsize=21),
        ("外界都说我们压力大", "我觉得吧压力也没有那么大", "主要是28岁了还没媳妇儿"),
    ),
    MultiArgMeme(
        ("你好骚啊",),
        "nihaosaoa.jpg",
        gif_func("nihaosaoa.gif", ((0, 14), (16, 26), (42, 61)), fontsize=17),
        ("既然追求刺激", "就贯彻到底了", "你好骚啊"),
    ),
    MultiArgMeme(
        ("食屎啦你",),
        "shishilani.jpg",
        gif_func(
            "shishilani.gif", ((14, 21), (23, 36), (38, 46), (60, 66)), fontsize=17
        ),
        ("穿西装打领带", "拿大哥大有什么用", "跟着这样的大哥", "食屎啦你"),
    ),
    MultiArgMeme(
        ("五年怎么过的",),
        "wunian.jpg",
        gif_func("wunian.gif", ((11, 20), (35, 50), (59, 77), (82, 95)), fontsize=16),
        ("五年", "你知道我这五年是怎么过的吗", "我每天躲在家里玩贪玩蓝月", "你知道有多好玩吗"),
    ),
]
