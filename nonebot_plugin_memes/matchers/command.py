import random
import traceback
from typing import Any, NoReturn, Union

from arclet.alconna import config as alc_config
from meme_generator import Meme
from meme_generator.exception import MemeGeneratorException
from nonebot import get_driver
from nonebot.adapters import Bot, Event
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
from nonebot_plugin_uninfo import Interface, QryItrface, Session, Uninfo, User

from ..config import memes_config
from ..manager import meme_manager
from ..recorder import record_meme_generation
from ..utils import NetworkError
from .utils import UserId

alc_config.command_max_count += 1000


async def process(
    bot: Bot,
    event: Event,
    state: T_State,
    matcher: Matcher,
    session: Session,
    meme: Meme,
    images: list[Image],
    texts: list[str],
    users: list[User],
    args: dict[str, Any] = {},
    show_info: bool = False,
):
    image_contents: list[bytes] = []

    try:
        for image in images:
            result = await image_fetch(event, bot, state, image)
            if not isinstance(result, bytes):
                raise NotImplementedError
            image_contents.append(result)
    except NotImplementedError:
        await matcher.finish("当前平台可能不支持获取图片")
    except (NetworkError, AdapterException):
        logger.warning(traceback.format_exc())
        await matcher.finish("图片下载出错，请稍后再试")

    args_user_infos = []
    for user in users:
        name = user.nick or user.name
        gender = user.gender
        if gender not in ("male", "female"):
            gender = "unknown"
        args_user_infos.append({"name": name, "gender": gender})
    args["user_infos"] = args_user_infos

    try:
        result = await run_sync(meme)(images=image_contents, texts=texts, args=args)
        await record_meme_generation(session, meme.key)
    except MemeGeneratorException as e:
        await matcher.finish(e.message)

    msg = UniMessage()
    if show_info:
        keywords = "、".join([f'"{keyword}"' for keyword in meme.keywords])
        msg += f"关键词：{keywords}"
    msg += UniMessage.image(raw=result)
    await msg.send()


T_MemeParams = Union[Text, Image, At]
meme_params_key = "meme_params"
arg_meme_params = Args[meme_params_key, MultiVar(T_MemeParams, "*")]


async def handle_params(
    matcher: Matcher,
    session: Session,
    interface: Interface,
    meme_params: list[T_MemeParams],
):
    texts: list[str] = []
    images: list[Image] = []
    users: list[User] = []

    for msg_seg in meme_params:
        if isinstance(msg_seg, At):
            try:
                user = None
                if session.scene.type > 0:
                    try:
                        if member := await interface.get_member(
                            session.scene.type, session.scene.id, msg_seg.target
                        ):
                            user = member.user
                            if member.nick:
                                user.nick = member.nick
                    except (NotImplementedError, NetworkError, AdapterException):
                        pass
                if not user:
                    user = await interface.get_user(msg_seg.target)
                if user:
                    if image_url := user.avatar:
                        images.append(Image(url=image_url))
                    users.append(user)
            except NotImplementedError:
                await matcher.finish("当前平台可能不支持获取用户信息")
            except (NetworkError, AdapterException):
                logger.warning(traceback.format_exc())
                await matcher.finish("用户信息获取出错，请稍后再试")

        elif isinstance(msg_seg, Image):
            images.append(msg_seg)

        elif isinstance(msg_seg, Text):
            text = msg_seg.text
            if text.startswith("@") and (user_id := text[1:]):
                try:
                    if user := await interface.get_user(user_id):
                        if image_url := user.avatar:
                            images.append(Image(url=image_url))
                        users.append(user)
                except NotImplementedError:
                    await matcher.finish("当前平台可能不支持获取用户信息")
                except (NetworkError, AdapterException):
                    logger.warning(traceback.format_exc())
                    await matcher.finish("用户信息获取出错，请检查用户 id 或稍后再试")

            elif text == "自己":
                user = session.user
                if image_url := user.avatar:
                    images.append(Image(url=image_url))
                if (member := session.member) and member.nick:
                    user.nick = member.nick
                users.append(user)

            elif text:
                texts.append(text)

    return texts, images, users


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
        session: Uninfo,
        interface: QryItrface,
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
        texts, images, users = await handle_params(
            matcher, session, interface, meme_params
        )

        # 当所需图片数为 2 且已指定图片数为 1 时，使用发送者的头像作为第一张图
        if meme.params_type.min_images == 2 and len(images) == 1:
            user = session.user
            if image_url := user.avatar:
                images.insert(0, Image(url=image_url))
            if (member := session.member) and member.nick:
                user.nick = member.nick
            users.insert(0, user)

        # 当所需图片数为 1 且没有已指定图片时，使用发送者的头像
        if memes_config.memes_use_sender_when_no_image and (
            meme.params_type.min_images == 1 and len(images) == 0
        ):
            user = session.user
            if image_url := user.avatar:
                images.append(Image(url=image_url))
            if (member := session.member) and member.nick:
                user.nick = member.nick
            users.append(user)

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
            meme.params_type.min_images <= len(images) <= meme.params_type.max_images
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
        await process(
            bot, event, state, matcher, session, meme, images, texts, users, args
        )


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
    session: Uninfo,
    interface: QryItrface,
    alc_matches: AlcMatches,
):
    meme_params: list[T_MemeParams] = list(alc_matches.query(meme_params_key, ()))
    texts, images, users = await handle_params(matcher, session, interface, meme_params)

    available_memes = [
        meme
        for meme in meme_manager.get_memes()
        if meme_manager.check(user_id, meme.key)
        and (
            (meme.params_type.min_images <= len(images) <= meme.params_type.max_images)
            and (meme.params_type.min_texts <= len(texts) <= meme.params_type.max_texts)
        )
    ]
    if not available_memes:
        await matcher.finish("找不到符合参数数量的表情")

    random_meme = random.choice(available_memes)
    await process(
        bot,
        event,
        state,
        matcher,
        session,
        random_meme,
        images,
        texts,
        users,
        show_info=memes_config.memes_random_meme_show_info,
    )
