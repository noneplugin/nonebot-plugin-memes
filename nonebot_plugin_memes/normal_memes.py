from typing import List
from datetime import datetime
from PIL.Image import Image as IMG

from nonebot_plugin_imageutils import BuildImage, Text2Image

from .depends import Arg
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
    text2image = Text2Image.from_text(
        text, 70, fontname="FZXS14", fill="black", spacing=30
    ).wrap(700)
    text2image.lines = text2image.lines[:5]
    text_img = text2image.to_image()
    text_img = BuildImage(text_img).rotate(-9.3, expand=True)

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
            max_fontsize=80,
            min_fontsize=30,
            fill=(238, 0, 0),
            stroke_ratio=1 / 15,
            stroke_fill=(255, 255, 153),
        )
    except ValueError:
        return OVER_LENGTH_MSG
    return frame.save_png()


def jichou(text: str = Arg()):
    date = datetime.today().strftime("%Y{}%m{}%d{}").format("年", "月", "日")
    text = f"{date} 晴\n{text}\n这个仇我先记下了"
    text2image = Text2Image.from_text(text, 45, fill="black", spacing=10).wrap(440)
    if len(text2image.lines) > 10:
        return OVER_LENGTH_MSG
    text_img = text2image.to_image()

    frame = load_image("jichou/0.png")
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


def diyu(text: str = Arg()):
    frame = load_image("diyu/0.png")
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


def scroll(text: str = Arg()):
    text2image = Text2Image.from_text(text, 40).wrap(600)
    if len(text2image.lines) > 5:
        return OVER_LENGTH_MSG
    text_img = text2image.to_image()
    text_w, text_h = text_img.size

    box_w = text_w + 140
    box_h = max(text_h + 103, 150)
    box = BuildImage.new("RGBA", (box_w, box_h))
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
    num = 20
    dy = int(dialog.height / num)
    for i in range(num):
        frame = BuildImage.new("RGBA", dialog.size)
        frame.paste(dialog, (0, -dy * i))
        frame.paste(dialog, (0, dialog.height - dy * i))
        frames.append(frame.image)
    return save_gif(frames, 0.02)
