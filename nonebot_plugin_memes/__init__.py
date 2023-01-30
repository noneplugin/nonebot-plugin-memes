from io import BytesIO
from PIL import ImageFilter
from typing import List, Union, Literal

from nonebot.params import Depends
from nonebot.utils import run_sync
from nonebot.matcher import Matcher
from nonebot.typing import T_Handler
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot import require, on_command, on_message
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageSegment,
    MessageEvent,
    GroupMessageEvent,
)
from nonebot.adapters.onebot.v11.permission import (
    GROUP_ADMIN,
    GROUP_OWNER,
    PRIVATE_FRIEND,
)

require("nonebot_plugin_imageutils")
from nonebot_plugin_imageutils import BuildImage, Text2Image

from .utils import Meme
from .depends import regex
from .data_source import memes
from .download import load_thumb
from .manager import meme_manager, ActionResult, MemeMode


__plugin_meta__ = PluginMetadata(
    name="文字表情包",
    description="生成文字类表情包",
    usage="触发方式：指令 + 文字 (部分表情包需要多段文字)\n发送“文字表情包”查看表情包列表",
    extra={
        "unique_name": "memes",
        "example": "鲁迅说 我没说过这句话\n举牌 aya大佬带带我",
        "author": "meetwq <meetwq@gmail.com>",
        "version": "0.3.10",
    },
)


PERM_EDIT = GROUP_ADMIN | GROUP_OWNER | PRIVATE_FRIEND | SUPERUSER
PERM_GLOBAL = SUPERUSER

help_cmd = on_command("文字表情包", aliases={"文字相关表情包", "文字相关表情制作"}, block=True, priority=12)
block_cmd = on_command("禁用文字表情", block=True, priority=12, permission=PERM_EDIT)
unblock_cmd = on_command("启用文字表情", block=True, priority=12, permission=PERM_EDIT)
block_cmd_gl = on_command("全局禁用文字表情", block=True, priority=12, permission=PERM_GLOBAL)
unblock_cmd_gl = on_command("全局启用文字表情", block=True, priority=12, permission=PERM_GLOBAL)


@run_sync
def help_image(user_id: str, memes: List[Meme]) -> BytesIO:
    def thumb_image(meme: Meme) -> BuildImage:
        thumb = load_thumb(f"{meme.name}.jpg")
        thumb = thumb.resize_canvas((200, thumb.height), bg_color="white")
        text = "/".join(meme.keywords)
        if not meme_manager.check(user_id, meme):
            text = f"[color=lightgrey]{text}[/color]"
            thumb = thumb.filter(ImageFilter.GaussianBlur(radius=3))
            thumb.paste(BuildImage.new("RGBA", thumb.size, (0, 0, 0, 64)), alpha=True)
        text_img = (
            Text2Image.from_bbcode_text(text, 24).wrap(200).to_image(padding=(5, 2))
        )
        text_img = BuildImage(text_img).resize_canvas(
            (200, text_img.height), bg_color="white"
        )
        frame = BuildImage.new("RGB", (200, thumb.height + text_img.height), "white")
        frame.paste(thumb).paste(text_img, (0, thumb.height), alpha=True)
        frame = frame.resize_canvas(
            (frame.width + 10, frame.height + 10), bg_color="white"
        )
        return frame

    num_per_line = 6
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


def get_user_id():
    def dependency(event: MessageEvent) -> str:
        return (
            f"group_{event.group_id}"
            if isinstance(event, GroupMessageEvent)
            else f"private_{event.user_id}"
        )

    return Depends(dependency)


def check_flag(meme: Meme):
    def dependency(user_id: str = get_user_id()) -> bool:
        return meme_manager.check(user_id, meme)

    return Depends(dependency)


@help_cmd.handle()
async def _(user_id: str = get_user_id()):
    img = await help_image(user_id, memes)
    if img:
        await help_cmd.finish(MessageSegment.image(img))


@block_cmd.handle()
async def _(
    matcher: Matcher, msg: Message = CommandArg(), user_id: str = get_user_id()
):
    meme_names = msg.extract_plain_text().strip().split()
    if not meme_names:
        matcher.block = False
        await matcher.finish()
    results = meme_manager.block(user_id, meme_names)
    messages = []
    for name, result in results.items():
        if result == ActionResult.SUCCESS:
            message = f"表情 {name} 禁用成功"
        elif result == ActionResult.NOTFOUND:
            message = f"表情 {name} 不存在！"
        else:
            message = f"表情 {name} 禁用失败"
        messages.append(message)
    await matcher.finish("\n".join(messages))


@unblock_cmd.handle()
async def _(
    matcher: Matcher, msg: Message = CommandArg(), user_id: str = get_user_id()
):
    meme_names = msg.extract_plain_text().strip().split()
    if not meme_names:
        matcher.block = False
        await matcher.finish()
    results = meme_manager.unblock(user_id, meme_names)
    messages = []
    for name, result in results.items():
        if result == ActionResult.SUCCESS:
            message = f"表情 {name} 启用成功"
        elif result == ActionResult.NOTFOUND:
            message = f"表情 {name} 不存在！"
        else:
            message = f"表情 {name} 启用失败"
        messages.append(message)
    await matcher.finish("\n".join(messages))


@block_cmd_gl.handle()
async def _(matcher: Matcher, msg: Message = CommandArg()):
    meme_names = msg.extract_plain_text().strip().split()
    if not meme_names:
        matcher.block = False
        await matcher.finish()
    results = meme_manager.change_mode(MemeMode.WHITE, meme_names)
    messages = []
    for name, result in results.items():
        if result == ActionResult.SUCCESS:
            message = f"表情 {name} 已设为白名单模式"
        elif result == ActionResult.NOTFOUND:
            message = f"表情 {name} 不存在！"
        else:
            message = f"表情 {name} 设置失败"
        messages.append(message)
    await matcher.finish("\n".join(messages))


@unblock_cmd_gl.handle()
async def _(matcher: Matcher, msg: Message = CommandArg()):
    meme_names = msg.extract_plain_text().strip().split()
    if not meme_names:
        matcher.block = False
        await matcher.finish()
    results = meme_manager.change_mode(MemeMode.BLACK, meme_names)
    messages = []
    for name, result in results.items():
        if result == ActionResult.SUCCESS:
            message = f"表情 {name} 已设为黑名单模式"
        elif result == ActionResult.NOTFOUND:
            message = f"表情 {name} 不存在！"
        else:
            message = f"表情 {name} 设置失败"
        messages.append(message)
    await matcher.finish("\n".join(messages))


def create_matchers():
    def handler(meme: Meme) -> T_Handler:
        async def handle(
            matcher: Matcher,
            flag: Literal[True] = check_flag(meme),
            res: Union[str, BytesIO] = Depends(meme.func),
        ):
            if not flag:
                return
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
