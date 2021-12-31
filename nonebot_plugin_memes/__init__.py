import shlex
import traceback
from typing import Type
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.typing import T_Handler, T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment
from nonebot.log import logger

from .data_source import make_meme, memes
from .download import DownloadError
from .functions import text_to_pic


__help__plugin_name__ = 'memes'
__des__ = '表情包制作'
memes_help = [f"{i}. {'/'.join(list(e['aliases']))}" +
              (f"，需要输入{e['arg_num']}段文字"
               if e.get('arg_num', 1) > 1 else ' xxx')
              for i, e in enumerate(memes.values(), start=1)]
meme_help = '\n'.join(memes_help)
__cmd__ = f'''
目前支持的表情包：
{meme_help}
'''.strip()
__example__ = '''
鲁迅说 我没说过这句话
王境泽 我就是饿死 死外边 不会吃你们一点东西 真香
'''.strip()
__usage__ = f'{__des__}\n\nUsage:\n{__cmd__}\n\nExamples:\n{__example__}'


help_cmd = on_command('表情包制作', priority=12)


@help_cmd.handle()
async def _(bot: Bot, event: Event, state: T_State):
    img = await text_to_pic(__usage__)
    if img:
        await help_cmd.finish(MessageSegment.image(img))


async def handle(matcher: Type[Matcher], event: Event, type: str):
    text = event.get_plaintext().strip()
    if not text:
        await matcher.finish()

    arg_num = memes[type].get('arg_num', 1)
    texts = [text] if arg_num == 1 else shlex.split(text)
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
        async def handler(bot: Bot, event: Event, state: T_State):
            await handle(matcher, event, style)
        return handler

    for type, params in memes.items():
        matcher = on_command(
            type, aliases=params['aliases'], priority=13)
        matcher.append_handler(create_handler(type))


create_matchers()
