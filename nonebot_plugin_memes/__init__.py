import copy
import traceback
from argparse import ArgumentError
from itertools import chain
from typing import Any, Dict, List, Type, Union

from meme_generator.exception import (
    ArgMismatch,
    ImageNumberMismatch,
    MemeGeneratorException,
    TextNumberMismatch,
    TextOrNameNotEnough,
    TextOverLength,
)
from meme_generator.meme import Meme
from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GMEvent
from nonebot.adapters.onebot.v11 import Message as V11Msg
from nonebot.adapters.onebot.v11 import MessageEvent as V11MEvent
from nonebot.adapters.onebot.v11 import MessageSegment as V11MsgSeg
from nonebot.adapters.onebot.v11.permission import (
    GROUP_ADMIN,
    GROUP_OWNER,
    PRIVATE_FRIEND,
)
from nonebot.adapters.onebot.v12 import Bot as V12Bot
from nonebot.adapters.onebot.v12 import ChannelMessageEvent as V12CMEvent
from nonebot.adapters.onebot.v12 import GroupMessageEvent as V12GMEvent
from nonebot.adapters.onebot.v12 import Message as V12Msg
from nonebot.adapters.onebot.v12 import MessageEvent as V12MEvent
from nonebot.adapters.onebot.v12 import MessageSegment as V12MsgSeg
from nonebot.adapters.onebot.v12.permission import PRIVATE
from nonebot.exception import AdapterException
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Depends
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_Handler, T_State
from pypinyin import Style, pinyin

from .depends import (
    IMAGE_SOURCES_KEY,
    TEXTS_KEY,
    USERS_KEY,
    split_msg_v11,
    split_msg_v12,
)
from .manager import ActionResult, MemeMode, meme_manager
from .rule import command_rule, regex_rule
from .utils import (
    ImageSource,
    NetworkError,
    PlatformUnsupportError,
    User,
    UserInfo,
    generate_help_image,
    meme_info,
)

__plugin_meta__ = PluginMetadata(
    name="表情包制作",
    description="制作各种沙雕表情包",
    usage="发送“表情包制作”查看表情包列表",
    extra={
        "unique_name": "memes",
        "author": "meetwq <meetwq@gmail.com>",
        "version": "0.4.0",
    },
)


PERM_EDIT = GROUP_ADMIN | GROUP_OWNER | PRIVATE_FRIEND | PRIVATE | SUPERUSER
PERM_GLOBAL = SUPERUSER

help_cmd = on_command("表情包制作", aliases={"头像表情包", "文字表情包"}, block=True, priority=11)
info_cmd = on_command("表情详情", aliases={"表情帮助", "表情示例"}, block=True, priority=11)
block_cmd = on_command("禁用表情", block=True, priority=11, permission=PERM_EDIT)
unblock_cmd = on_command("启用表情", block=True, priority=11, permission=PERM_EDIT)
block_cmd_gl = on_command("全局禁用表情", block=True, priority=11, permission=PERM_GLOBAL)
unblock_cmd_gl = on_command("全局启用表情", block=True, priority=11, permission=PERM_GLOBAL)


def get_user_id():
    def dependency(
        bot: Union[V11Bot, V12Bot], event: Union[V11MEvent, V12MEvent]
    ) -> str:
        if isinstance(event, V11MEvent):
            cid = f"{bot.self_id}_{event.message_type}_"
        else:
            cid = f"{bot.self_id}_{event.detail_type}_"

        if isinstance(event, V11GMEvent) or isinstance(event, V12GMEvent):
            cid += str(event.group_id)
        elif isinstance(event, V12CMEvent):
            cid += f"{event.guild_id}_{event.channel_id}"
        else:
            cid += str(event.user_id)
        return cid

    return Depends(dependency)


@help_cmd.handle()
async def _(bot: Union[V11Bot, V12Bot], matcher: Matcher, user_id: str = get_user_id()):
    memes = sorted(
        meme_manager.memes,
        key=lambda meme: "".join(
            chain.from_iterable(pinyin(meme.keywords[0], style=Style.TONE3))
        ),
    )
    meme_list = [(meme, meme_manager.check(user_id, meme.key)) for meme in memes]
    img = await generate_help_image(meme_list)

    if isinstance(bot, V11Bot):
        await matcher.finish(V11MsgSeg.image(img))
    else:
        resp = await bot.upload_file(type="data", name="memes", data=img.getvalue())
        file_id = resp["file_id"]
        await matcher.finish(V12MsgSeg.image(file_id))


@info_cmd.handle()
async def _(
    bot: Union[V11Bot, V12Bot],
    matcher: Matcher,
    msg: Union[V11Msg, V12Msg] = CommandArg(),
):
    meme_name = msg.extract_plain_text().strip()
    if not meme_name:
        matcher.block = False
        await matcher.finish()

    if not (meme := meme_manager.find(meme_name)):
        await matcher.finish(f"表情 {meme_name} 不存在！")

    info = meme_info(meme)
    info += "表情预览：\n"
    img = await meme.generate_preview()

    if isinstance(bot, V11Bot):
        await matcher.finish(info + V11MsgSeg.image(img))
    else:
        resp = await bot.upload_file(type="data", name="memes", data=img.getvalue())
        file_id = resp["file_id"]
        await matcher.finish(info + V12MsgSeg.image(file_id))


@block_cmd.handle()
async def _(
    matcher: Matcher,
    msg: Union[V11Msg, V12Msg] = CommandArg(),
    user_id: str = get_user_id(),
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
    matcher: Matcher,
    msg: Union[V11Msg, V12Msg] = CommandArg(),
    user_id: str = get_user_id(),
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
async def _(matcher: Matcher, msg: Union[V11Msg, V12Msg] = CommandArg()):
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
async def _(matcher: Matcher, msg: Union[V11Msg, V12Msg] = CommandArg()):
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


def handler(meme: Meme) -> T_Handler:
    async def handle(
        bot: Union[V11Bot, V12Bot],
        state: T_State,
        matcher: Matcher,
        user_id: str = get_user_id(),
    ):
        if not meme_manager.check(user_id, meme.key):
            return

        raw_texts: List[str] = state[TEXTS_KEY]
        users: List[User] = state[USERS_KEY]
        image_sources: List[ImageSource] = state[IMAGE_SOURCES_KEY]

        images: List[bytes] = []
        texts: List[str] = []
        args: Dict[str, Any] = {}
        user_infos: List[UserInfo] = []

        if meme.params_type.args_type and (parser := meme.params_type.args_type.parser):
            parser = copy.deepcopy(parser)
            parser.add_argument("texts", nargs="*", default=[])
            try:
                parse_result = vars(parser.parse_args(raw_texts))
            except (ArgumentError, SystemExit) as e:
                logger.warning(f"参数解析错误: {e}")
                return
            texts = parse_result["texts"]
            parse_result.pop("texts")
            args = parse_result
        else:
            texts = raw_texts

        if not (
            (
                meme.params_type.min_images
                <= len(image_sources)
                <= meme.params_type.max_images
            )
            and (meme.params_type.min_texts <= len(texts) <= meme.params_type.max_texts)
        ):
            logger.info("输入 图片/文字 数量不符，跳过表情制作")
            return

        matcher.stop_propagation()

        try:
            for image_source in image_sources:
                images.append(await image_source.get_image())
        except PlatformUnsupportError as e:
            await matcher.finish(f"当前平台 “{e.platform}” 暂不支持获取头像，请使用图片输入")
        except (NetworkError, AdapterException):
            logger.warning(traceback.format_exc())
            await matcher.finish("图片下载出错，请稍后再试")

        try:
            for user in users:
                user_infos.append(await user.get_info())
            args["user_infos"] = user_infos
        except (NetworkError, AdapterException):
            logger.warning("用户信息获取失败\n" + traceback.format_exc())

        try:
            result = await meme(images=images, texts=texts, args=args)
        except ImageNumberMismatch:
            await matcher.finish(
                f"图片数量不符，图片数量应为 {meme.params_type.min_images}"
                + (
                    f" ~ {meme.params_type.max_images}"
                    if meme.params_type.max_images > meme.params_type.min_images
                    else ""
                )
            )
        except TextNumberMismatch:
            await matcher.finish(
                f"文字数量不符，文字数量应为 {meme.params_type.min_images}"
                + (
                    f" ~ {meme.params_type.max_images}"
                    if meme.params_type.max_images > meme.params_type.min_images
                    else ""
                )
            )
        except TextOverLength as e:
            await matcher.finish(f"文字 “{e.text}” 长度过长")
        except ArgMismatch:
            await matcher.finish("参数解析错误")
        except TextOrNameNotEnough:
            await matcher.finish("文字或名字数量不足")
        except MemeGeneratorException:
            logger.warning(traceback.format_exc())
            await matcher.finish("出错了，请稍后再试")

        if isinstance(bot, V11Bot):
            await matcher.finish(V11MsgSeg.image(result))
        else:
            resp = await bot.upload_file(
                type="data", name="memes", data=result.getvalue()
            )
            file_id = resp["file_id"]
            await matcher.finish(V12MsgSeg.image(file_id))

    return handle


def create_matchers():
    for meme in meme_manager.memes:
        matchers: List[Type[Matcher]] = []
        if meme.keywords:
            # 纯文字输入的表情，在命令后加空格以防止误触发
            keywords = (
                [keyword.rstrip() + " " for keyword in meme.keywords]
                if meme.params_type.min_images == 0 and meme.params_type.max_images == 0
                else meme.keywords
            )
            matchers.append(
                on_message(command_rule(keywords), block=False, priority=12)
            )
        if meme.patterns:
            matchers.append(
                on_message(regex_rule(meme.patterns), block=False, priority=12)
            )

        for matcher in matchers:
            matcher.append_handler(handler(meme), parameterless=[split_msg_v11(meme)])
            matcher.append_handler(handler(meme), parameterless=[split_msg_v12(meme)])


create_matchers()
