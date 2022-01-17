import shlex
import traceback
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.typing import T_Handler
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.log import logger

from .data_source import make_meme, memes
from .download import DownloadError
from .utils import help_image


__help__plugin_name__ = 'memes'
__des__ = '表情包制作'
__cmd__ = '发送“表情包制作”查看表情包列表'
__short_cmd__ = __cmd__
__example__ = '''
鲁迅说 我没说过这句话
王境泽 我就是饿死 死外边 不会吃你们一点东西 真香
'''.strip()
__usage__ = f'{__des__}\n\nUsage:\n{__cmd__}\n\nExamples:\n{__example__}'


help_cmd = on_command('表情包制作', block=True, priority=12)


@help_cmd.handle()
async def _():
    img = await help_image()
    if img:
        await help_cmd.finish(MessageSegment.image(img))


async def handle(matcher: Matcher, type: str, text: str):
    arg_num = memes[type].get('arg_num', 1)
    if arg_num == 1:
        texts = [text]
    else:
        try:
            texts = shlex.split(text)
        except:
            await matcher.finish(f'参数解析错误，若包含特殊符号请转义或加引号')

    if len(texts) < arg_num:
        await matcher.finish(f'该表情包需要输入{arg_num}段文字')
    elif len(texts) > arg_num:
        await matcher.finish(f'参数数量不符，需要输入{arg_num}段文字，若包含空格请加引号')

    try:
        msg = await make_meme(type, texts)
    except DownloadError:
        logger.warning(traceback.format_exc())
        await matcher.finish('资源下载出错，请稍后再试')
    except:
        logger.warning(traceback.format_exc())
        await matcher.finish('出错了，请稍后再试')

    if not msg:
        await matcher.finish('出错了，请稍后再试')
    if isinstance(msg, str):
        await matcher.finish(msg)
    else:
        await matcher.finish(MessageSegment.image(msg))


def create_matchers():

    def create_handler(style: str) -> T_Handler:
        async def handler(msg: Message = CommandArg()):
            text = msg.extract_plain_text().strip()
            if not text:
                await matcher.finish()
            await handle(matcher, style, text)
        return handler

    for type, params in memes.items():
        matcher = on_command(type, aliases=params['aliases'],
                             block=True, priority=13)
        matcher.append_handler(create_handler(type))


create_matchers()
