import random
import traceback
from typing import Any, NoReturn, Union

from arclet.alconna import config as alc_config
from meme_generator import Meme
from meme_generator.exception import MemeGeneratorException
from nonebot import get_driver
from nonebot.adapters import Bot, Event
from nonebot.compat import PYDANTIC_V2, ConfigDict
from nonebot.exception import AdapterException
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.utils import run_sync
from nonebot_plugin_alconna import (
    AlcMatches,
    Alconna,
    Args,
    At,
    CommandMeta,
    Image,
    MultiVar,
    Text,
    UniMessage,
    on_alconna,
)
from nonebot_plugin_alconna.builtins.extensions.reply import ReplyMergeExtension
from nonebot_plugin_alconna.uniseg.tools import image_fetch
from nonebot_plugin_session import EventSession, Session
from nonebot_plugin_userinfo import ImageSource, UserInfo, get_user_info

from ..config import memes_config
from ..manager import meme_manager
from ..recorder import record_meme_generation
from ..utils import NetworkError
from .utils import UserId

alc_config.command_max_count += 1000


async def process(
    matcher: Matcher,
    session: Session,
    meme: Meme,
    image_sources: list[ImageSource],
    texts: list[str],
    user_infos: list[UserInfo],
    args: dict[str, Any] = {},
    show_info: bool = False,
):
    images: list[bytes] = []

    try:
        for image_source in image_sources:
            images.append(await image_source.get_image())
    except NotImplementedError:
        await matcher.finish("当前平台可能不支持获取图片")
    except (NetworkError, AdapterException):
        logger.warning(traceback.format_exc())
        await matcher.finish("图片下载出错，请稍后再试")

    args_user_infos = []
    for user_info in user_infos:
        name = user_info.user_displayname or user_info.user_name
        gender = str(user_info.user_gender)
        if gender not in ("male", "female"):
            gender = "unknown"
        args_user_infos.append({"name": name, "gender": gender})
    args["user_infos"] = args_user_infos

    try:
        result = await run_sync(meme)(images=images, texts=texts, args=args)
        await record_meme_generation(session, meme.key)
    except MemeGeneratorException as e:
        await matcher.finish(e.message)

    msg = UniMessage()
    if show_info:
        keywords = "、".join([f'"{keyword}"' for keyword in meme.keywords])
        msg += f"关键词：{keywords}"
    msg += UniMessage.image(raw=result)
    await msg.send()


class AlcImage(ImageSource):
    bot: Bot
    event: Event
    state: T_State
    img: Image

    if PYDANTIC_V2:
        model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)
    else:

        class Config:
            arbitrary_types_allowed: bool = True

    async def get_image(self) -> bytes:
        result = await image_fetch(self.event, self.bot, self.state, self.img)
        if isinstance(result, bytes):
            return result
        raise NotImplementedError("image fetch not implemented")


T_MemeParams = Union[Text, Image, At]
meme_params_key = "meme_params"
arg_meme_params = Args[meme_params_key, MultiVar(T_MemeParams, "*")]


async def handle_params(
    bot: Bot, event: Event, state: T_State, meme_params: list[T_MemeParams]
):
    texts: list[str] = []
    image_sources: list[ImageSource] = []
    user_infos: list[UserInfo] = []

    for msg_seg in meme_params:
        if isinstance(msg_seg, At):
            if user_info := await get_user_info(bot, event, msg_seg.target):
                if image_source := user_info.user_avatar:
                    image_sources.append(image_source)
                user_infos.append(user_info)

        elif isinstance(msg_seg, Image):
            image_sources.append(
                AlcImage(bot=bot, event=event, state=state, img=msg_seg)
            )

        elif isinstance(msg_seg, Text):
            text = msg_seg.text
            if text.startswith("@") and (user_id := text[1:]):
                if user_info := await get_user_info(bot, event, user_id):
                    if image_source := user_info.user_avatar:
                        image_sources.append(image_source)
                    user_infos.append(user_info)

            elif text == "自己":
                if user_info := await get_user_info(bot, event, event.get_user_id()):
                    if image_source := user_info.user_avatar:
                        image_sources.append(image_source)
                    user_infos.append(user_info)

            elif text:
                texts.append(text)

    return texts, image_sources, user_infos


prefixes = list(get_driver().config.command_start)
if (meme_prefixes := memes_config.memes_command_prefixes) is not None:
    prefixes = meme_prefixes


def create_matcher(meme: Meme):
    options = [
        opt.option()
        for opt in (
            meme.params_type.args_type.parser_options
            if meme.params_type.args_type
            else []
        )
    ]
    meme_matcher = on_alconna(
        Alconna(
            prefixes,
            meme.keywords[0],
            *options,
            arg_meme_params,
            meta=CommandMeta(keep_crlf=True),
        ),
        aliases=set(meme.keywords[1:]),
        block=False,
        priority=12,
        extensions=[ReplyMergeExtension()],
    )
    for shortcut in meme.shortcuts:
        meme_matcher.shortcut(
            shortcut.key,
            arguments=shortcut.args,
            prefix=True,
            humanized=shortcut.humanized,
        )

    @meme_matcher.handle()
    async def _(
        bot: Bot,
        event: Event,
        state: T_State,
        matcher: Matcher,
        user_id: UserId,
        session: EventSession,
        alc_matches: AlcMatches,
    ):
        if not meme_manager.check(user_id, meme.key):
            logger.info(f"用户 {user_id} 表情 {meme.key} 被禁用")
            return

        args: dict[str, Any] = {}
        options = alc_matches.options
        for option, option_result in options.items():
            if option_result.value is None:
                args.update(option_result.args)
            else:
                args[option] = option_result.value

        meme_params: list[T_MemeParams] = list(alc_matches.query(meme_params_key, ()))
        texts, image_sources, user_infos = await handle_params(
            bot, event, state, meme_params
        )

        # 当所需图片数为 2 且已指定图片数为 1 时，使用发送者的头像作为第一张图
        if meme.params_type.min_images == 2 and len(image_sources) == 1:
            if user_info := await get_user_info(bot, event, event.get_user_id()):
                if image_source := user_info.user_avatar:
                    image_sources.insert(0, image_source)
                user_infos.insert(0, user_info)

        # 当所需图片数为 1 且没有已指定图片时，使用发送者的头像
        if memes_config.memes_use_sender_when_no_image and (
            meme.params_type.min_images == 1 and len(image_sources) == 0
        ):
            if user_info := await get_user_info(bot, event, event.get_user_id()):
                if image_source := user_info.user_avatar:
                    image_sources.append(image_source)
                user_infos.append(user_info)

        # 当所需文字数 >0 且没有输入文字时，使用默认文字
        if memes_config.memes_use_default_when_no_text and (
            meme.params_type.min_texts > 0 and len(texts) == 0
        ):
            texts = meme.params_type.default_texts

        async def finish(msg: str) -> NoReturn:
            logger.info(msg)
            if memes_config.memes_prompt_params_error:
                matcher.stop_propagation()
                await matcher.finish(msg)
            await matcher.finish()

        if not (
            meme.params_type.min_images
            <= len(image_sources)
            <= meme.params_type.max_images
        ):
            await finish(
                f"输入图片数量不符，图片数量应为 {meme.params_type.min_images}"
                + (
                    f" ~ {meme.params_type.max_images}"
                    if meme.params_type.max_images > meme.params_type.min_images
                    else ""
                )
            )
        if not (meme.params_type.min_texts <= len(texts) <= meme.params_type.max_texts):
            await finish(
                f"输入文字数量不符，文字数量应为 {meme.params_type.min_texts}"
                + (
                    f" ~ {meme.params_type.max_texts}"
                    if meme.params_type.max_texts > meme.params_type.min_texts
                    else ""
                )
            )

        matcher.stop_propagation()
        await process(matcher, session, meme, image_sources, texts, user_infos, args)


def create_matchers():
    for meme in meme_manager.get_memes():
        create_matcher(meme)


create_matchers()


random_matcher = on_alconna(
    Alconna("随机表情", arg_meme_params),
    block=False,
    priority=12,
    use_cmd_start=True,
    extensions=[ReplyMergeExtension()],
)


@random_matcher.handle()
async def _(
    bot: Bot,
    event: Event,
    state: T_State,
    matcher: Matcher,
    user_id: UserId,
    session: EventSession,
    alc_matches: AlcMatches,
):
    meme_params: list[T_MemeParams] = list(alc_matches.query(meme_params_key, ()))
    texts, image_sources, user_infos = await handle_params(
        bot, event, state, meme_params
    )

    available_memes = [
        meme
        for meme in meme_manager.get_memes()
        if meme_manager.check(user_id, meme.key)
        and (
            (
                meme.params_type.min_images
                <= len(image_sources)
                <= meme.params_type.max_images
            )
            and (meme.params_type.min_texts <= len(texts) <= meme.params_type.max_texts)
        )
    ]
    if not available_memes:
        await matcher.finish("找不到符合参数数量的表情")

    random_meme = random.choice(available_memes)
    await process(
        matcher,
        session,
        random_meme,
        image_sources,
        texts,
        user_infos,
        show_info=memes_config.memes_random_meme_show_info,
    )
