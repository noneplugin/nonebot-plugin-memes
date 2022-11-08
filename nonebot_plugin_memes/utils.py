from io import BytesIO
from dataclasses import dataclass
from PIL.Image import Image as IMG
from typing import List, Tuple, Callable

OVER_LENGTH_MSG = "文字长度过长，请适当缩减"


def save_gif(frames: List[IMG], duration: float) -> BytesIO:
    output = BytesIO()
    frames[0].save(
        output,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=duration * 1000,
        loop=0,
        disposal=2,
    )
    return output


@dataclass
class Meme:
    name: str
    func: Callable
    keywords: Tuple[str, ...]
    pattern: str = ""

    def __post_init__(self):
        if not self.pattern:
            self.pattern = rf"(?:{'|'.join(self.keywords)})\s+"


@dataclass
class GifMeme(Meme):
    def __post_init__(self):
        p_kw = "|".join(self.keywords)
        self.pattern = rf"(?:{p_kw})[\s\.]*gif"
        self.keywords = tuple(f"{k}.gif" for k in self.keywords)
