from typing import List, Tuple
from datetime import datetime
from typing_extensions import Literal
from PIL.Image import Image as IMG

from nonebot_plugin_imageutils import BuildImage, Text2Image

from .depends import *
from .download import load_image
from .utils import save_gif, OVER_LENGTH_MSG


def luxunsay(text: str = Arg()):
    frame = load_image("luxunsay/0.jpg")
    try:
        frame.draw_text(
            (40, frame.height - 200, frame.width - 40, frame.height - 100),
            text,
            allow_wrap=True,
            max_fontsize=40,
            min_fontsize=30,
            fill="white",
        )
    except ValueError:
        return OVER_LENGTH_MSG
    luxun_text = Text2Image.from_text("--鲁迅", 30, fill="white").to_image()
    frame.paste(luxun_text, (320, 400), alpha=True)
    return frame.save_png()


def nokia(text: str = Arg()):
    text = text[:900]
    text_img = (
        Text2Image.from_text(text, 70, fontname="FZXS14", fill="black", spacing=30)
        .wrap(700)
        .to_image()
    )
    text_img = (
        BuildImage(text_img)
        .resize_canvas((700, 450), direction="northwest")
        .rotate(-9.3, expand=True)
    )

    head_img = Text2Image.from_text(
        f"{len(text)}/900", 70, fontname="FZXS14", fill=(129, 212, 250, 255)
    ).to_image()
    head_img = BuildImage(head_img).rotate(-9.3, expand=True)

    frame = load_image("nokia/0.jpg")
    frame.paste(text_img, (205, 330), alpha=True)
    frame.paste(head_img, (790, 320), alpha=True)
    return frame.save_jpg()


def goodnews(text: str = Arg()):
    frame = load_image("goodnews/0.jpg")
    try:
        frame.draw_text(
            (50, 100, frame.width - 50, frame.height - 100),
            text,
            allow_wrap=True,
            lines_align="center",
            max_fontsize=50,
            min_fontsize=30,
            fill=(238, 0, 0),
            stroke_ratio=1 / 15,
            stroke_fill=(255, 255, 153),
        )
    except ValueError:
        return OVER_LENGTH_MSG
    return frame.save_png()


def holdgrudge(text: str = Arg()):
    date = datetime.today().strftime("%Y{}%m{}%d{}").format("年", "月", "日")
    text = f"{date} 晴\n{text}\n这个仇我先记下了"
    text2image = Text2Image.from_text(text, 45, fill="black", spacing=10).wrap(440)
    if len(text2image.lines) > 10:
        return OVER_LENGTH_MSG
    text_img = text2image.to_image()

    frame = load_image("holdgrudge/0.png")
    bg = BuildImage.new(
        "RGB", (frame.width, frame.height + text_img.height + 20), "white"
    )
    bg.paste(frame).paste(text_img, (30, frame.height + 5), alpha=True)
    return bg.save_jpg()


def fanatic(text: str = Arg()):
    frame = load_image("fanatic/0.jpg")
    try:
        frame.draw_text(
            (145, 40, 343, 160),
            text,
            allow_wrap=True,
            lines_align="center",
            max_fontsize=70,
            min_fontsize=30,
        )
    except ValueError:
        return OVER_LENGTH_MSG
    return frame.save_jpg()


def murmur(text: str = Arg()):
    frame = load_image("murmur/0.png")
    try:
        frame.draw_text(
            (10, 255, 430, 300),
            text,
            max_fontsize=40,
            min_fontsize=20,
        )
    except ValueError:
        return OVER_LENGTH_MSG
    return frame.save_png()


def shutup(text: str = Arg()):
    frame = load_image("shutup/0.jpg")
    try:
        frame.draw_text(
            (10, 180, 230, 230),
            text,
            allow_wrap=True,
            max_fontsize=40,
            min_fontsize=20,
        )
    except ValueError:
        return OVER_LENGTH_MSG
    return frame.save_jpg()


def slap(text: str = Arg()):
    frame = load_image("slap/0.jpg")
    try:
        frame.draw_text(
            (20, 450, 620, 630),
            text,
            allow_wrap=True,
            max_fontsize=110,
            min_fontsize=65,
        )
    except ValueError:
        return OVER_LENGTH_MSG
    return frame.save_jpg()


def imprison(text: str = Arg()):
    frame = load_image("imprison/0.jpg")
    try:
        frame.draw_text(
            (10, 157, 230, 197),
            text,
            allow_wrap=True,
            max_fontsize=35,
            min_fontsize=15,
        )
    except ValueError:
        return OVER_LENGTH_MSG
    return frame.save_jpg()


def scroll(text: str = Arg()):
    text2image = Text2Image.from_text(text, 40).wrap(600)
    if len(text2image.lines) > 5:
        return OVER_LENGTH_MSG
    text_img = text2image.to_image()
    text_w, text_h = text_img.size

    box_w = text_w + 140
    box_h = max(text_h + 103, 150)
    box = BuildImage.new("RGBA", (box_w, box_h), "#eaedf4")
    corner1 = load_image("scroll/corner1.png")
    corner2 = load_image("scroll/corner2.png")
    corner3 = load_image("scroll/corner3.png")
    corner4 = load_image("scroll/corner4.png")
    box.paste(corner1, (0, 0))
    box.paste(corner2, (0, box_h - 75))
    box.paste(corner3, (text_w + 70, 0))
    box.paste(corner4, (text_w + 70, box_h - 75))
    box.paste(BuildImage.new("RGBA", (text_w, box_h - 40), "white"), (70, 20))
    box.paste(BuildImage.new("RGBA", (text_w + 88, box_h - 150), "white"), (27, 75))
    box.paste(text_img, (70, 17 + (box_h - 40 - text_h) // 2), alpha=True)

    dialog = BuildImage.new("RGBA", (box_w, box_h * 4), "#eaedf4")
    for i in range(4):
        dialog.paste(box, (0, box_h * i))

    frames: List[IMG] = []
    num = 30
    dy = int(dialog.height / num)
    for i in range(num):
        frame = BuildImage.new("RGBA", dialog.size)
        frame.paste(dialog, (0, -dy * i))
        frame.paste(dialog, (0, dialog.height - dy * i))
        frames.append(frame.image)
    return save_gif(frames, 0.05)


def high_EQ(left: str = RegexArg("left"), right: str = RegexArg("right"), arg=NoArg()):
    frame = load_image("high_EQ/0.jpg")

    def draw(pos: Tuple[float, float, float, float], text: str):
        frame.draw_text(
            pos,
            text,
            max_fontsize=100,
            min_fontsize=50,
            allow_wrap=True,
            fill="white",
            stroke_fill="black",
            stroke_ratio=0.05,
        )

    try:
        draw((40, 540, 602, 1140), left)
        draw((682, 540, 1244, 1140), right)
    except ValueError:
        return OVER_LENGTH_MSG
    return frame.save_jpg()


def wujing(left: str = RegexArg("left"), right: str = RegexArg("right"), arg=NoArg()):
    frame = load_image("wujing/0.jpg")

    def draw(
        pos: Tuple[float, float, float, float],
        text: str,
        align: Literal["left", "right", "center"],
    ):
        frame.draw_text(
            pos,
            text,
            halign=align,
            max_fontsize=100,
            min_fontsize=50,
            fill="white",
            stroke_fill="black",
            stroke_ratio=0.05,
        )

    try:
        if left:
            parts = left.split()
            if len(parts) >= 2:
                draw((50, 430, 887, 550), " ".join(parts[:-1]), "left")
            draw((20, 560, 350, 690), parts[-1], "right")
        if right:
            parts = right.split()
            draw((610, 540, 917, 670), parts[0], "left")
            if len(parts) >= 2:
                draw((50, 680, 887, 810), " ".join(parts[1:]), "center")
    except ValueError:
        return OVER_LENGTH_MSG
    return frame.save_jpg()


def slogan(texts: List[str] = Args(6)):
    frame = load_image("slogan/0.jpg")

    def draw(pos: Tuple[float, float, float, float], text: str):
        frame.draw_text(pos, text, max_fontsize=40, min_fontsize=20, allow_wrap=True)

    try:
        draw((10, 0, 294, 50), texts[0])
        draw((316, 0, 602, 50), texts[1])
        draw((10, 230, 294, 280), texts[2])
        draw((316, 230, 602, 280), texts[3])
        draw((10, 455, 294, 505), texts[4])
        draw((316, 455, 602, 505), texts[5])
    except ValueError:
        return OVER_LENGTH_MSG
    return frame.save_jpg()


def wakeup(text: str = RegexArg("text"), arg=NoArg()):
    frame = load_image("wakeup/0.jpg")
    try:
        frame.draw_text((310, 270, 460, 380), text, max_fontsize=90, min_fontsize=50)
        frame.draw_text(
            (50, 610, 670, 720), f"{text}起来了", max_fontsize=110, min_fontsize=70
        )
    except ValueError:
        return
    return frame.save_jpg()


def raisesign(text: str = Arg()):
    frame = load_image("raisesign/0.jpg")
    text_img = BuildImage.new("RGBA", (360, 260))
    try:
        text_img.draw_text(
            (10, 10, 350, 250),
            text,
            max_fontsize=80,
            min_fontsize=40,
            allow_wrap=True,
            lines_align="center",
            spacing=10,
            fontname="FZSEJW",
            fill="#51201b",
        )
    except ValueError:
        return OVER_LENGTH_MSG
    text_img = text_img.perspective(((33, 0), (375, 120), (333, 387), (0, 258)))
    frame.paste(text_img, (285, 24), alpha=True)
    return frame.save_jpg()


def psyduck(texts: List[str] = Args(2)):
    left_img = BuildImage.new("RGBA", (155, 100))
    right_img = BuildImage.new("RGBA", (155, 100))

    def draw(frame: BuildImage, text: str):
        frame.draw_text(
            (5, 5, 150, 95),
            text,
            max_fontsize=80,
            min_fontsize=30,
            allow_wrap=True,
            fontname="FZSJ-QINGCRJ",
        )

    try:
        draw(left_img, texts[0])
        draw(right_img, texts[1])
    except ValueError:
        return OVER_LENGTH_MSG

    params = [
        ("left", ((0, 11), (154, 0), (161, 89), (20, 104)), (18, 42)),
        ("left", ((0, 9), (153, 0), (159, 89), (20, 101)), (15, 38)),
        ("left", ((0, 7), (148, 0), (156, 89), (21, 97)), (14, 23)),
        None,
        ("right", ((10, 0), (143, 17), (124, 104), (0, 84)), (298, 18)),
        ("right", ((13, 0), (143, 27), (125, 113), (0, 83)), (298, 30)),
        ("right", ((13, 0), (143, 27), (125, 113), (0, 83)), (298, 26)),
        ("right", ((13, 0), (143, 27), (125, 113), (0, 83)), (298, 30)),
        ("right", ((13, 0), (143, 27), (125, 113), (0, 83)), (302, 20)),
        ("right", ((13, 0), (141, 23), (120, 102), (0, 82)), (300, 24)),
        ("right", ((13, 0), (140, 22), (118, 100), (0, 82)), (299, 22)),
        ("right", ((9, 0), (128, 16), (109, 89), (0, 80)), (303, 23)),
        None,
        ("left", ((0, 13), (152, 0), (158, 89), (17, 109)), (35, 36)),
        ("left", ((0, 13), (152, 0), (158, 89), (17, 109)), (31, 29)),
        ("left", ((0, 17), (149, 0), (155, 90), (17, 120)), (45, 33)),
        ("left", ((0, 14), (152, 0), (156, 91), (17, 115)), (40, 27)),
        ("left", ((0, 12), (154, 0), (158, 90), (17, 109)), (35, 28)),
    ]

    frames: List[IMG] = []
    for i in range(18):
        frame = load_image(f"psyduck/{i}.jpg")
        param = params[i]
        if param:
            side, points, pos = param
            if side == "left":
                frame.paste(left_img.perspective(points), pos, alpha=True)
            elif side == "right":
                frame.paste(right_img.perspective(points), pos, alpha=True)
        frames.append(frame.image)
    return save_gif(frames, 0.2)
