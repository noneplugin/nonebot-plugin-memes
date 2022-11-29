import math
import random
from PIL import Image
from datetime import datetime
from PIL.Image import Image as IMG
from typing import List, Tuple, Literal
from PIL.Image import Transform, Resampling

from nonebot_plugin_imageutils import BuildImage, Text2Image
from nonebot_plugin_imageutils.gradient import ColorStop, LinearGradient

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
            max_fontsize=60,
            min_fontsize=30,
            fill=(238, 0, 0),
            stroke_ratio=1 / 15,
            stroke_fill=(255, 255, 153),
        )
    except ValueError:
        return OVER_LENGTH_MSG
    return frame.save_png()


def badnews(text: str = Arg()):
    frame = load_image("badnews/0.png")
    try:
        frame.draw_text(
            (50, 100, frame.width - 50, frame.height - 100),
            text,
            allow_wrap=True,
            lines_align="center",
            max_fontsize=60,
            min_fontsize=30,
            fill=(0, 0, 0),
            stroke_ratio=1 / 15,
            stroke_fill="white",
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
            min_fontsize=15,
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
            min_fontsize=15,
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
            min_fontsize=50,
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


def slogan(texts: List[str] = Args(6, prompt=True)):
    frame = load_image("slogan/0.jpg")

    def draw(pos: Tuple[float, float, float, float], text: str):
        frame.draw_text(pos, text, max_fontsize=40, min_fontsize=15, allow_wrap=True)

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
            min_fontsize=30,
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


def psyduck(texts: List[str] = Args(2, prompt=True)):
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


def scratchoff(text: str = Arg()):
    frame = load_image("scratchoff/0.png")
    try:
        frame.draw_text(
            (80, 160, 360, 290),
            text,
            allow_wrap=True,
            max_fontsize=80,
            min_fontsize=30,
            fill="white",
            lines_align="center",
        )
    except ValueError:
        return OVER_LENGTH_MSG
    mask = load_image("scratchoff/1.png")
    frame.paste(mask, alpha=True)
    return frame.save_jpg()


def ascension(text: str = Arg()):
    frame = load_image("ascension/0.png")
    text = f"你原本应该要去地狱的，但因为你生前{text}，我们就当作你已经服完刑期了"
    try:
        frame.draw_text(
            (40, 30, 482, 135),
            text,
            allow_wrap=True,
            max_fontsize=50,
            min_fontsize=20,
        )
    except ValueError:
        return OVER_LENGTH_MSG
    return frame.save_jpg()


def run(text: str = Arg()):
    frame = load_image("run/0.png")
    text_img = BuildImage.new("RGBA", (122, 53))
    try:
        text_img.draw_text(
            (0, 0, 122, 53),
            text,
            allow_wrap=True,
            max_fontsize=50,
            min_fontsize=10,
            lines_align="center",
        )
    except ValueError:
        return OVER_LENGTH_MSG
    frame.paste(text_img.rotate(7, expand=True), (200, 195), alpha=True)
    return frame.save_jpg()


def meteor(text: str = Arg()):
    frame = load_image("meteor/0.png")
    try:
        frame.draw_text(
            (220, 230, 920, 315),
            text,
            allow_wrap=True,
            max_fontsize=80,
            min_fontsize=20,
            fill="white",
        )
    except ValueError:
        return OVER_LENGTH_MSG
    return frame.save_jpg()


def wish_fail(text: str = Arg()):
    frame = load_image("wish_fail/0.png")
    try:
        frame.draw_text(
            (70, 305, 320, 380),
            text,
            allow_wrap=True,
            max_fontsize=80,
            min_fontsize=20,
        )
    except ValueError:
        return OVER_LENGTH_MSG
    return frame.save_jpg()


def findchips(texts: List[str] = Args(4, prompt=True)):
    frame = load_image("findchips/0.jpg")

    def draw(pos: Tuple[float, float, float, float], text: str):
        frame.draw_text(pos, text, max_fontsize=40, min_fontsize=20, allow_wrap=True)

    try:
        draw((405, 54, 530, 130), texts[0])
        draw((570, 62, 667, 160), texts[1])
        draw((65, 400, 325, 463), texts[2])
        draw((430, 400, 630, 470), texts[3])
    except ValueError:
        return OVER_LENGTH_MSG
    return frame.save_jpg()


def bronya_holdsign(text: str = Arg()):
    frame = load_image("bronya_holdsign/0.jpg")
    try:
        frame.draw_text(
            (190, 675, 640, 930),
            text,
            fill=(111, 95, 95),
            allow_wrap=True,
            max_fontsize=60,
            min_fontsize=25,
        )
    except ValueError:
        return OVER_LENGTH_MSG
    return frame.save_jpg()


def pornhub(texts: List[str] = Args(2, prompt=True)):
    left_img = Text2Image.from_text(texts[0], fontsize=200, fill="white").to_image(
        bg_color="black", padding=(20, 10)
    )

    right_img = Text2Image.from_text(
        texts[1], fontsize=200, fill="black", weight="bold"
    ).to_image(bg_color=(247, 152, 23), padding=(20, 10))
    right_img = BuildImage(right_img).circle_corner(20)

    frame = BuildImage.new(
        "RGBA",
        (left_img.width + right_img.width, max(left_img.height, right_img.height)),
        "black",
    )
    frame.paste(left_img, (0, frame.height - left_img.height)).paste(
        right_img, (left_img.width, frame.height - right_img.height), alpha=True
    )
    frame = frame.resize_canvas(
        (frame.width + 100, frame.height + 100), bg_color="black"
    )
    return frame.save_jpg()


def youtube(texts: List[str] = Args(2, prompt=True)):
    left_img = Text2Image.from_text(texts[0], fontsize=200, fill="black").to_image(
        bg_color="white", padding=(30, 20)
    )

    right_img = Text2Image.from_text(
        texts[1], fontsize=200, fill="white", weight="bold"
    ).to_image(bg_color=(230, 33, 23), padding=(50, 20))
    right_img = BuildImage(right_img).resize_canvas(
        (max(right_img.width, 400), right_img.height), bg_color=(230, 33, 23)
    )
    right_img = right_img.circle_corner(right_img.height // 2)

    frame = BuildImage.new(
        "RGBA",
        (left_img.width + right_img.width, max(left_img.height, right_img.height)),
        "white",
    )
    frame.paste(left_img, (0, frame.height - left_img.height))
    frame = frame.resize_canvas(
        (frame.width + 100, frame.height + 100), bg_color="white"
    )

    corner = load_image("youtube/corner.png")
    ratio = right_img.height / 2 / corner.height
    corner = corner.resize((int(corner.width * ratio), int(corner.height * ratio)))
    x0 = left_img.width + 50
    y0 = frame.height - right_img.height - 50
    x1 = frame.width - corner.width - 50
    y1 = frame.height - corner.height - 50
    frame.paste(corner, (x0, y0 - 1), alpha=True).paste(
        corner.transpose(Image.FLIP_TOP_BOTTOM), (x0, y1 + 1), alpha=True
    ).paste(corner.transpose(Image.FLIP_LEFT_RIGHT), (x1, y0 - 1), alpha=True).paste(
        corner.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT),
        (x1, y1 + 1),
        alpha=True,
    ).paste(
        right_img, (x0, y0), alpha=True
    )
    return frame.save_jpg()


def google(text: str = Arg()):
    text = " ".join(text.splitlines())
    colors = ["#4285f4", "#db4437", "#f4b400", "#4285f4", "#0f9d58", "#db4437"]
    t2m = Text2Image.from_text(text, 200)
    index = 0
    for char in t2m.lines[0].chars:
        char.fill = colors[index % len(colors)]
        if char.char.strip():
            index += 1
    return BuildImage(t2m.to_image(bg_color="white", padding=(50, 50))).save_jpg()


def fivethousand_choyen(texts: List[str] = Args(2, prompt=True)):
    fontsize = 200
    fontname = "Noto Sans SC"
    text = texts[0]
    pos_x = 40
    pos_y = 220
    imgs: List[Tuple[IMG, Tuple[int, int]]] = []

    def transform(img: IMG) -> IMG:
        skew = 0.45
        dw = round(img.height * skew)
        return img.transform(
            (img.width + dw, img.height),
            Transform.AFFINE,
            (1, skew, -dw, 0, 1, 0),
            Resampling.BILINEAR,
        )

    def shift(t2m: Text2Image) -> Tuple[int, int]:
        return (
            pos_x
            - t2m.lines[0].chars[0].stroke_width
            - max(char.stroke_width for char in t2m.lines[0].chars),
            pos_y - t2m.lines[0].ascent,
        )

    def add_color_text(stroke_width: int, fill: str, pos: Tuple[int, int]):
        t2m = Text2Image.from_text(
            text, fontsize, fontname=fontname, stroke_width=stroke_width, fill=fill
        )
        dx, dy = shift(t2m)
        imgs.append((transform(t2m.to_image()), (dx + pos[0], dy + pos[1])))

    def add_gradient_text(
        stroke_width: int,
        dir: Tuple[int, int, int, int],
        color_stops: List[Tuple[float, Tuple[int, int, int]]],
        pos: Tuple[int, int],
    ):
        t2m = Text2Image.from_text(
            text, fontsize, fontname=fontname, stroke_width=stroke_width, fill="white"
        )
        mask = transform(t2m.to_image()).convert("L")
        dx, dy = shift(t2m)
        gradient = LinearGradient(
            (dir[0] - dx, dir[1] - dy, dir[2] - dx, dir[3] - dy),
            [ColorStop(*color_stop) for color_stop in color_stops],
        )
        bg = gradient.create_image(mask.size)
        bg.putalpha(mask)
        imgs.append((bg, (dx + pos[0], dy + pos[1])))

    # 黑
    add_color_text(22, "black", (8, 8))
    # 银
    add_gradient_text(
        20,
        (0, 38, 0, 234),
        [
            (0.0, (0, 15, 36)),
            (0.1, (255, 255, 255)),
            (0.18, (55, 58, 59)),
            (0.25, (55, 58, 59)),
            (0.5, (200, 200, 200)),
            (0.75, (55, 58, 59)),
            (0.85, (25, 20, 31)),
            (0.91, (240, 240, 240)),
            (0.95, (166, 175, 194)),
            (1, (50, 50, 50)),
        ],
        (8, 8),
    )
    # 黑
    add_color_text(16, "black", (0, 0))
    # 金
    add_gradient_text(
        10,
        (0, 40, 0, 200),
        [
            (0, (253, 241, 0)),
            (0.25, (245, 253, 187)),
            (0.4, (255, 255, 255)),
            (0.75, (253, 219, 9)),
            (0.9, (127, 53, 0)),
            (1, (243, 196, 11)),
        ],
        (0, 0),
    )
    # 黑
    add_color_text(6, "black", (4, -6))
    # 白
    add_color_text(6, "white", (0, -6))
    # 红
    add_gradient_text(
        4,
        (0, 50, 0, 200),
        [
            (0, (255, 100, 0)),
            (0.5, (123, 0, 0)),
            (0.51, (240, 0, 0)),
            (1, (5, 0, 0)),
        ],
        (0, -6),
    )
    # 红
    add_gradient_text(
        0,
        (0, 50, 0, 200),
        [
            (0, (230, 0, 0)),
            (0.5, (123, 0, 0)),
            (0.51, (240, 0, 0)),
            (1, (5, 0, 0)),
        ],
        (0, -6),
    )

    text = texts[1]
    fontname = "Noto Serif SC"
    pos_x = 300
    pos_y = 480
    # 黑
    add_color_text(22, "black", (10, 4))
    # 银
    add_gradient_text(
        19,
        (0, 320, 0, 506),
        [
            (0, (0, 15, 36)),
            (0.25, (250, 250, 250)),
            (0.5, (150, 150, 150)),
            (0.75, (55, 58, 59)),
            (0.85, (25, 20, 31)),
            (0.91, (240, 240, 240)),
            (0.95, (166, 175, 194)),
            (1, (50, 50, 50)),
        ],
        (10, 4),
    )
    # 黑
    add_color_text(17, "#10193A", (0, 0))
    # 白
    add_color_text(8, "#D0D0D0", (0, 0))
    # 绀
    add_gradient_text(
        7,
        (0, 320, 0, 480),
        [
            (0, (16, 25, 58)),
            (0.03, (255, 255, 255)),
            (0.08, (16, 25, 58)),
            (0.2, (16, 25, 58)),
            (1, (16, 25, 58)),
        ],
        (0, 0),
    )
    # 银
    add_gradient_text(
        0,
        (0, 320, 0, 480),
        [
            (0, (245, 246, 248)),
            (0.15, (255, 255, 255)),
            (0.35, (195, 213, 220)),
            (0.5, (160, 190, 201)),
            (0.51, (160, 190, 201)),
            (0.52, (196, 215, 222)),
            (1.0, (255, 255, 255)),
        ],
        (0, -6),
    )

    img_h = 580
    img_w = max([img.width + pos[0] for img, pos in imgs])
    frame = BuildImage.new("RGBA", (img_w, img_h), "white")
    for img, pos in imgs:
        frame.paste(img, pos, alpha=True)
    return frame.save_jpg()


def douyin(text: str = Arg()):
    text = " ".join(text.splitlines())
    fontsize = 200
    offset = round(fontsize * 0.05)
    px = 70
    py = 30
    bg_color = "#1C0B1B"
    frame = Text2Image.from_text(
        text, fontsize, fill="#FF0050", stroke_fill="#FF0050", stroke_width=5
    ).to_image(bg_color=bg_color, padding=(px + offset * 2, py + offset * 2, px, py))
    Text2Image.from_text(
        text, fontsize, fill="#00F5EB", stroke_fill="#00F5EB", stroke_width=5
    ).draw_on_image(frame, (px, py))
    Text2Image.from_text(
        text, fontsize, fill="white", stroke_fill="white", stroke_width=5
    ).draw_on_image(frame, (px + offset, py + offset))
    frame = BuildImage(frame)

    width = frame.width - px
    height = frame.height - py
    frame_num = 10
    devide_num = 6
    seed = 20 * 0.05
    frames: List[IMG] = []
    for _ in range(frame_num):
        new_frame = frame.copy()
        h_seeds = [
            math.fabs(math.sin(random.random() * devide_num)) for _ in range(devide_num)
        ]
        h_seed_sum = sum(h_seeds)
        h_seeds = [s / h_seed_sum for s in h_seeds]
        direction = 1
        last_yn = 0
        last_h = 0
        for i in range(devide_num):
            yn = last_yn + last_h
            h = max(round(height * h_seeds[i]), 2)
            last_yn = yn
            last_h = h
            direction = -direction
            piece = new_frame.copy().crop((px, yn, px + width, yn + h))
            new_frame.paste(piece, (px + round(i * direction * seed), yn))
        # 透视变换
        move_x = 64
        points = (
            (move_x, 0),
            (new_frame.width + move_x, 0),
            (new_frame.width, new_frame.height),
            (0, new_frame.height),
        )
        new_frame = new_frame.perspective(points)
        bg = BuildImage.new("RGBA", new_frame.size, bg_color)
        bg.paste(new_frame, alpha=True)
        frames.append(bg.image)

    return save_gif(frames, 0.2)


def not_call_me(text: str = Arg()):
    frame = load_image("not_call_me/0.png")
    try:
        frame.draw_text(
            (228, 11, 340, 164),
            text,
            allow_wrap=True,
            max_fontsize=80,
            min_fontsize=20,
        )
    except ValueError:
        return OVER_LENGTH_MSG
    return frame.save_png()
