from io import BytesIO
from typing import List
from PIL.Image import Image as IMG
from PIL import Image, ImageDraw

from .static_meme import static_memes
from .gif_meme import gif_memes
from .functions import wrap_text, load_thumb, load_font, save_jpg, DEFAULT_FONT


async def static_thumb_image(name: str, thumbnail: str) -> IMG:
    frame = Image.new('RGB', (200, 235), (255, 255, 255))
    thumb = await load_thumb(thumbnail)
    img_w, img_h = thumb.size
    frame.paste(thumb, (100 - int(img_w / 2), 100 - int(img_h / 2)))
    font = await load_font(DEFAULT_FONT, 16)
    text_w, _ = font.getsize(name)
    draw = ImageDraw.Draw(frame)
    draw.text((100 - text_w / 2, 205), name, font=font, fill='black')
    draw.rectangle(((0, 0), (199, 234)), fill=None, outline='grey', width=1)
    return frame


async def gif_thumb_image(name: str, thumbnail: str, examples: List[str]) -> IMG:
    frame = Image.new('RGB', (415, 235), (255, 255, 255))
    thumb = await load_thumb(thumbnail)
    img_w, img_h = thumb.size
    frame.paste(thumb, (100 - int(img_w / 2), 100 - int(img_h / 2)))
    font = await load_font(DEFAULT_FONT, 16)
    draw = ImageDraw.Draw(frame)
    text_w, _ = font.getsize(name)
    draw.text((100 - text_w / 2, 205), name, font=font, fill='black')

    examples = wrap_text('\n'.join(examples), font, 200)
    examples = '\n'.join(examples)
    text_w, text_h = font.getsize_multiline(examples)
    draw.multiline_text((315 - text_w / 2, (235 - text_h) / 2),
                        examples, font=font, fill='grey')
    draw.rectangle(((0, 0), (414, 234)), fill=None, outline='grey', width=1)
    for y in range(0, 235, 20):
        draw.line([(207, y), (207, y + 10)], fill='grey', width=1)
    return frame


async def static_help_image() -> IMG:
    static_thumbs = []
    for meme in static_memes.values():
        name = '/'.join(list(meme['aliases']))
        thumb = await static_thumb_image(name, meme['thumbnail'])
        static_thumbs.append(thumb)
    static_thumbs = [static_thumbs[i:i + 4]
                     for i in range(0, len(static_thumbs), 4)]

    frame = Image.new('RGB', (875, 250 * len(static_thumbs) + 15),
                      (255, 255, 255))
    for row, line in enumerate(static_thumbs):
        for col, thumb in enumerate(line):
            frame.paste(thumb, (215 * col + 15, 250 * row + 15))
    return frame


async def gif_help_image() -> IMG:
    gif_thumbs = []
    for meme in gif_memes.values():
        name = '/'.join(list(meme['aliases']))
        examples = meme['examples']
        examples = [f'{i}.{e}' for i, e in enumerate(examples, start=1)]
        examples.insert(0, f'需要{len(examples)}段文字，示例：')
        thumb = await gif_thumb_image(name, meme['thumbnail'], examples)
        gif_thumbs.append(thumb)
    gif_thumbs = [gif_thumbs[i:i + 2]
                  for i in range(0, len(gif_thumbs), 2)]

    frame = Image.new('RGB', (875, 250 * len(gif_thumbs) + 15),
                      (255, 255, 255))
    for row, line in enumerate(gif_thumbs):
        for col, thumb in enumerate(line):
            frame.paste(thumb, (430 * col + 15, 250 * row + 15))
    return frame


async def help_image() -> BytesIO:
    image1 = await static_help_image()
    image2 = await gif_help_image()
    w1, h1 = image1.size
    w2, h2 = image2.size
    frame = Image.new('RGB', (max(w1, w2), h1 + h2), (255, 255, 255))
    frame.paste(image1, (0, 0))
    frame.paste(image2, (0, h1))
    return save_jpg(frame)
