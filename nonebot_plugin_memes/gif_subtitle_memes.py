from functools import partial
from typing import List, Tuple

from nonebot_plugin_imageutils import BuildImage

from .depends import Args
from .download import load_image
from .utils import save_gif, OVER_LENGTH_MSG


def make_gif(
    filename: str,
    pieces: Tuple[Tuple[int, int], ...],
    examples: Tuple[str, ...],
    texts: List[str] = Args(),
    fontsize: int = 20,
    padding_x: int = 5,
    padding_y: int = 5,
):
    if not texts:
        texts = list(examples)

    if len(texts) != len(pieces):
        return f"该表情包需要加{len(pieces)}段文字，不加可查看示例图片"

    img = load_image(f"gif/{filename}").image
    frames: List[BuildImage] = []
    for i in range(img.n_frames):
        img.seek(i)
        frames.append(BuildImage(img.convert("RGB")))

    parts = [frames[start:end] for start, end in pieces]
    for part, text in zip(parts, texts):
        for frame in part:
            try:
                frame.draw_text(
                    (padding_x, 0, frame.width - padding_x, frame.height - padding_y),
                    text,
                    max_fontsize=fontsize,
                    min_fontsize=fontsize,
                    fill="white",
                    stroke_ratio=0.05,
                    stroke_fill="black",
                    valign="bottom",
                )
            except ValueError:
                return OVER_LENGTH_MSG

    return save_gif([frame.image for frame in frames], img.info["duration"] / 1000)


def gif_func(
    filename: str,
    pieces: Tuple[Tuple[int, int], ...],
    examples: Tuple[str, ...],
    **kwargs,
):
    return partial(
        make_gif, filename=filename, pieces=pieces, examples=examples, **kwargs
    )


wangjingze = gif_func(
    "wangjingze.gif",
    ((0, 9), (12, 24), (25, 35), (37, 48)),
    ("我就是饿死", "死外边 从这里跳下去", "不会吃你们一点东西", "真香"),
)

# fmt: off
weisuoyuwei = gif_func(
    "weisuoyuwei.gif",
    ((11, 14), (27, 38), (42, 61), (63, 81), (82, 95), (96, 105), (111, 131), (145, 157), (157, 167),),
    ("好啊", "就算你是一流工程师", "就算你出报告再完美", "我叫你改报告你就要改", "毕竟我是客户", "客户了不起啊", "Sorry 客户真的了不起", "以后叫他天天改报告", "天天改 天天改"),
    fontsize=19,
)
# fmt: on

chanshenzi = gif_func(
    "chanshenzi.gif",
    ((0, 16), (16, 31), (33, 40)),
    ("你那叫喜欢吗？", "你那是馋她身子", "你下贱！"),
    fontsize=18,
)

qiegewala = gif_func(
    "qiegewala.gif",
    ((0, 15), (16, 31), (31, 38), (38, 48), (49, 68), (68, 86)),
    ("没有钱啊 肯定要做的啊", "不做的话没有钱用", "那你不会去打工啊", "有手有脚的", "打工是不可能打工的", "这辈子不可能打工的"),
)

shuifandui = gif_func(
    "shuifandui.gif",
    ((3, 14), (21, 26), (31, 38), (40, 45)),
    ("我话说完了", "谁赞成", "谁反对", "我反对"),
    fontsize=19,
)

zengxiaoxian = gif_func(
    "zengxiaoxian.gif",
    ((3, 15), (24, 30), (30, 46), (56, 63)),
    ("平时你打电子游戏吗", "偶尔", "星际还是魔兽", "连连看"),
    fontsize=21,
)

yalidaye = gif_func(
    "yalidaye.gif",
    ((0, 16), (21, 47), (52, 77)),
    ("外界都说我们压力大", "我觉得吧压力也没有那么大", "主要是28岁了还没媳妇儿"),
    fontsize=21,
)

nihaosaoa = gif_func(
    "nihaosaoa.gif",
    ((0, 14), (16, 26), (42, 61)),
    ("既然追求刺激", "就贯彻到底了", "你好骚啊"),
    fontsize=17,
)

shishilani = gif_func(
    "shishilani.gif",
    ((14, 21), (23, 36), (38, 46), (60, 66)),
    ("穿西装打领带", "拿大哥大有什么用", "跟着这样的大哥", "食屎啦你"),
    fontsize=17,
)

wunian = gif_func(
    "wunian.gif",
    ((11, 20), (35, 50), (59, 77), (82, 95)),
    ("五年", "你知道我这五年是怎么过的吗", "我每天躲在家里玩贪玩蓝月", "你知道有多好玩吗"),
    fontsize=16,
)
