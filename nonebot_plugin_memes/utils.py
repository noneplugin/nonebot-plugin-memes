import imageio
from io import BytesIO
from dataclasses import dataclass
from PIL.Image import Image as IMG
from typing import List, Tuple, Callable

from nonebot.utils import run_sync
from nonebot_plugin_imageutils import BuildImage, Text2Image

from .download import load_thumb

OVER_LENGTH_MSG = "文字长度过长，请适当缩减"


def save_gif(frames: List[IMG], duration: float) -> BytesIO:
    output = BytesIO()
    imageio.mimsave(output, frames, format="gif", duration=duration)
    return output


@dataclass
class Meme:
    key: str
    func: Callable
    keywords: Tuple[str, ...]
    pattern: str = ""

    def __post_init__(self):
        if not self.pattern:
            self.pattern = "|".join(self.keywords)


@dataclass
class GifMeme(Meme):
    def __post_init__(self):
        p_kw = "|".join(self.keywords)
        self.pattern = rf"(?:{p_kw})[\s\.]*gif"
        self.keywords = tuple(f"{k}.gif" for k in self.keywords)


def thumb_image(meme: Meme) -> BuildImage:
    thumb = load_thumb(f"{meme.key}.jpg")
    thumb = thumb.resize_canvas((200, thumb.height), bg_color="white")
    text = "/".join(meme.keywords)
    text_img = Text2Image.from_text(text, 24).wrap(200).to_image(padding=(5, 2))
    text_img = BuildImage(text_img).resize_canvas(
        (200, text_img.height), bg_color="white"
    )
    frame = BuildImage.new("RGB", (200, thumb.height + text_img.height), "white")
    frame.paste(thumb).paste(text_img, (0, thumb.height), alpha=True)
    frame = frame.resize_canvas((frame.width + 10, frame.height + 10), bg_color="white")
    return frame


@run_sync
def help_image(memes: List[Meme]) -> BytesIO:
    num_per_line = 5
    line_imgs: List[BuildImage] = []
    for i in range(0, len(memes), num_per_line):
        imgs = [thumb_image(meme) for meme in memes[i : i + num_per_line]]
        line_w = sum([img.width for img in imgs])
        line_h = max([img.height for img in imgs])
        line_img = BuildImage.new("RGB", (line_w, line_h), "white")
        current_x = 0
        for img in imgs:
            line_img.paste(img, (current_x, line_h - img.height))
            current_x += img.width
        line_imgs.append(line_img)
    img_w = max([img.width for img in line_imgs])
    img_h = sum([img.height for img in line_imgs])
    frame = BuildImage.new("RGB", (img_w, img_h), "white")
    current_y = 0
    for img in line_imgs:
        frame.paste(img, (0, current_y))
        current_y += img.height
    frame = frame.resize_canvas((frame.width + 20, frame.height + 20), bg_color="white")
    return frame.save_jpg()
