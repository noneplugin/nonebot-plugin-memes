from io import BytesIO
from typing import List
from PIL.Image import Image as IMG
from PIL import Image, ImageDraw

from .data_source import memes
from .functions import wrap_text, load_thumb, load_font, save_jpg, DEFAULT_FONT


async def thumb_image(name: str, thumbnail: str, examples: List[str] = []) -> IMG:
    thumb_w = 415 if examples else 200

    frame = Image.new('RGB', (thumb_w, 235), (255, 255, 255))
    thumb = await load_thumb(thumbnail)
    img_w, img_h = thumb.size
    frame.paste(thumb, (100 - int(img_w / 2), 100 - int(img_h / 2)))
    font = await load_font(DEFAULT_FONT, 22)
    draw = ImageDraw.Draw(frame)
    text_w, _ = font.getsize(name)
    draw.text((100 - text_w / 2, 202), name, font=font, fill='black')

    if examples:
        example_font = await load_font(DEFAULT_FONT, 16)
        examples = [f'{i}.{e}' for i, e in enumerate(examples, start=1)]
        examples.insert(0, f'需要{len(examples)}段文字，示例：')
        examples = wrap_text('\n'.join(examples), example_font, 200)
        examples = '\n'.join(examples)
        text_w, text_h = example_font.getsize_multiline(examples)
        draw.multiline_text((307 - text_w / 2, (235 - text_h) / 2),
                            examples, font=example_font, fill='grey')
        draw.rectangle(((0, 0), (414, 234)), fill=None,
                       outline='grey', width=1)
        for y in range(0, 235, 20):
            draw.line([(200, y), (200, y + 10)], fill='grey', width=1)
    else:
        draw.rectangle(((0, 0), (199, 234)),
                       fill=None, outline='grey', width=1)
    return frame


async def help_image_part(memes: List[dict], have_examples: bool = False) -> IMG:
    thumbs = []
    num_per_line = 2 if have_examples else 4
    w_per_thumb = 430 if have_examples else 215

    for meme in memes:
        name = '/'.join(list(meme['aliases']))
        thumb = await thumb_image(name, meme['thumbnail'],
                                  meme['examples'] if have_examples else [])
        thumbs.append(thumb)
    thumbs = [thumbs[i:i + num_per_line]
              for i in range(0, len(thumbs), num_per_line)]

    frame = Image.new('RGB', (875, 250 * len(thumbs) + 15), (255, 255, 255))
    for row, line in enumerate(thumbs):
        for col, thumb in enumerate(line):
            frame.paste(thumb, (w_per_thumb * col + 15, 250 * row + 15))
    return frame


async def help_image() -> BytesIO:
    memes_part1 = []
    memes_part2 = []
    for meme in memes.values():
        if meme.get('examples', []):
            memes_part2.append(meme)
        else:
            memes_part1.append(meme)

    image1 = await help_image_part(memes_part1, have_examples=False)
    image2 = await help_image_part(memes_part2, have_examples=True)
    w1, h1 = image1.size
    w2, h2 = image2.size
    frame = Image.new('RGB', (max(w1, w2), h1 + h2), (255, 255, 255))
    frame.paste(image1, (0, 0))
    frame.paste(image2, (0, h1))
    return save_jpg(frame)
