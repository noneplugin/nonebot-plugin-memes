from PIL import Image, ImageDraw
from .data_source import load_font, DEFAULT_FONT, save_jpg


async def text_to_pic(text: str, fontsize: int = 30, padding: int = 50,
                      bg_color=(255, 255, 255), font_color=(0, 0, 0)):
    font = await load_font(DEFAULT_FONT, fontsize)
    text_w, text_h = font.getsize_multiline(text)

    frame = Image.new('RGB', (text_w + padding * 2,
                      text_h + padding * 2), bg_color)
    draw = ImageDraw.Draw(frame)
    draw.multiline_text((padding, padding), text, font=font, fill=font_color)
    return save_jpg(frame)
