from io import BytesIO
from typing import List, Union

from .normal_meme import normal_memes
from .gif_subtitle_meme import gif_subtitle_memes


memes = {**normal_memes, **gif_subtitle_memes}


async def make_meme(type: str, texts: List[str]) -> Union[str, BytesIO]:
    return await memes[type]['func'](texts)
