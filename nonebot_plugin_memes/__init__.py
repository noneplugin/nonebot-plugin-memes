from io import BytesIO
from typing import Union
from nonebot.params import Depends
from nonebot.matcher import Matcher
from nonebot.typing import T_Handler
from nonebot import on_command, on_message, require
from nonebot.adapters.onebot.v11 import MessageSegment

require("nonebot_plugin_imageutils")

from .depends import regex
from .data_source import memes
from .utils import Meme, help_image

__help__plugin_name__ = "memes"
__des__ = "表情包制作"
__cmd__ = "发送“表情包制作”查看表情包列表"
__short_cmd__ = __cmd__
__example__ = """
鲁迅说 我没说过这句话
王境泽.gif 我就是饿死 死外边 不会吃你们一点东西 真香
""".strip()
__usage__ = f"{__des__}\n\nUsage:\n{__cmd__}\n\nExamples:\n{__example__}"


help_cmd = on_command("表情包制作", block=True, priority=12)


@help_cmd.handle()
async def _():
    img = await help_image(memes)
    if img:
        await help_cmd.finish(MessageSegment.image(img))


def create_matchers():
    def handler(meme: Meme) -> T_Handler:
        async def handle(
            matcher: Matcher, res: Union[str, BytesIO] = Depends(meme.func)
        ):
            matcher.stop_propagation()
            if isinstance(res, str):
                await matcher.finish(res)
            await matcher.finish(MessageSegment.image(res))

        return handle

    for meme in memes:
        on_message(
            regex(meme.pattern),
            block=False,
            priority=12,
        ).append_handler(handler(meme))


create_matchers()
