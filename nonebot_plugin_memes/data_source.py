from io import BytesIO
from typing import List, Union

from .static_meme import static_memes
from .gif_meme import gif_memes


memes = {**static_memes, **gif_memes}


async def make_meme(type: str, texts: List[str]) -> Union[str, BytesIO]:
    return await memes[type]['func'](texts)
