import asyncio
import hashlib
import math
import shlex
from dataclasses import dataclass
from io import BytesIO
from typing import List, Tuple, TypedDict, Union

import httpx
from meme_generator.meme import Meme
from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GMEvent
from nonebot.adapters.onebot.v11 import MessageEvent as V11MEvent
from nonebot.adapters.onebot.v12 import Bot as V12Bot
from nonebot.adapters.onebot.v12 import ChannelMessageEvent as V12CMEvent
from nonebot.adapters.onebot.v12 import GroupMessageEvent as V12GMEvent
from nonebot.adapters.onebot.v12 import MessageEvent as V12MEvent
from nonebot.log import logger
from nonebot.utils import run_sync
from PIL.Image import Image as IMG
from pil_utils import BuildImage, Text2Image

from .config import memes_config


class NetworkError(Exception):
    pass


async def download_url(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.get(url, timeout=20)
                resp.raise_for_status()
                return resp.content
            except Exception as e:
                logger.warning(f"Error downloading {url}, retry {i}/3: {e}")
                await asyncio.sleep(3)
    raise NetworkError(f"{url} 下载失败！")


@dataclass
class ImageSource:
    async def get_image(self) -> bytes:
        raise NotImplementedError


@dataclass
class ImageUrl(ImageSource):
    url: str

    async def get_image(self) -> bytes:
        return await download_url(self.url)


@dataclass
class QQAvatar(ImageSource):
    qq: str

    async def get_image(self) -> bytes:
        url = f"http://q1.qlogo.cn/g?b=qq&nk={self.qq}&s=640"
        data = await download_url(url)
        if hashlib.md5(data).hexdigest() == "acef72340ac0e914090bd35799f5594e":
            url = f"http://q1.qlogo.cn/g?b=qq&nk={self.qq}&s=100"
            data = await download_url(url)
        return data


class PlatformUnsupportError(Exception):
    def __init__(self, platform: str):
        self.platform = platform


@dataclass
class UnsupportAvatar(ImageSource):
    platform: str

    async def get_image(self) -> bytes:
        raise PlatformUnsupportError(self.platform)


def user_avatar(
    bot: Union[V11Bot, V12Bot], event: Union[V11MEvent, V12MEvent], user_id: str
) -> ImageSource:
    if isinstance(bot, V11Bot):
        return QQAvatar(qq=user_id)

    assert isinstance(event, V12MEvent)
    platform = bot.platform
    if platform == "qq":
        return QQAvatar(qq=user_id)

    return UnsupportAvatar(platform)


def check_user_id(bot: Union[V11Bot, V12Bot], user_id: str) -> bool:
    platform = "qq" if isinstance(bot, V11Bot) else bot.platform

    if platform == "qq":
        return user_id.isdigit() and 11 >= len(user_id) >= 5

    return False


class UserInfo(TypedDict):
    name: str
    gender: str


@dataclass
class User:
    async def get_info(self) -> UserInfo:
        raise NotImplementedError


@dataclass
class V11User(User):
    bot: V11Bot
    event: V11MEvent
    user_id: int

    async def get_info(self) -> UserInfo:
        if isinstance(self.event, V11GMEvent):
            info = await self.bot.get_group_member_info(
                group_id=self.event.group_id, user_id=self.user_id
            )
        else:
            info = await self.bot.get_stranger_info(user_id=self.user_id)
        name = info.get("card", "") or info.get("nickname", "")
        gender = info.get("sex", "")
        return UserInfo(name=name, gender=gender)


@dataclass
class V12User(User):
    bot: V12Bot
    event: V12MEvent
    user_id: str

    async def get_info(self) -> UserInfo:
        if isinstance(self.event, V12GMEvent):
            info = await self.bot.get_group_member_info(
                group_id=self.event.group_id, user_id=self.user_id
            )
        elif isinstance(self.event, V12CMEvent):
            info = await self.bot.get_guild_member_info(
                guild_id=self.event.guild_id, user_id=self.user_id
            )
        else:
            info = await self.bot.get_user_info(user_id=self.user_id)
        name = info.get("user_displayname", "") or info.get("user_name", "")
        gender = "unknown"
        return UserInfo(name=name, gender=gender)


def split_text(text: str) -> List[str]:
    try:
        return shlex.split(text)
    except:
        return text.split()


def meme_info(meme: Meme) -> str:
    keywords = "、".join([f'"{keyword}"' for keyword in meme.keywords])

    patterns = "、".join([f'"{pattern}"' for pattern in meme.patterns])

    image_num = f"{meme.params_type.min_images}"
    if meme.params_type.max_images > meme.params_type.min_images:
        image_num += f" ~ {meme.params_type.max_images}"

    text_num = f"{meme.params_type.min_texts}"
    if meme.params_type.max_texts > meme.params_type.min_texts:
        text_num += f" ~ {meme.params_type.max_texts}"

    default_texts = ", ".join([f'"{text}"' for text in meme.params_type.default_texts])

    if args := meme.params_type.args_type:
        parser = args.parser
        args_info = parser.format_help().split("\n\n")[-1]
        lines = []
        for line in args_info.splitlines():
            if line.lstrip().startswith("options") or line.lstrip().startswith(
                "-h, --help"
            ):
                continue
            lines.append(line)
        args_info = "\n".join(lines)
    else:
        args_info = ""

    return (
        f"表情名：{meme.key}\n"
        + f"关键词：{keywords}\n"
        + (f"正则表达式：{patterns}\n" if patterns else "")
        + f"需要图片数目：{image_num}\n"
        + f"需要文字数目：{text_num}\n"
        + (f"默认文字：[{default_texts}]\n" if default_texts else "")
        + (f"可选参数：\n{args_info}\n" if args_info else "")
    )


@run_sync
def generate_help_image(meme_list: List[Tuple[Meme, bool]]) -> BytesIO:
    def cmd_text(memes: List[Tuple[Meme, bool]], start: int = 1) -> str:
        texts = []
        for i, (meme, status) in enumerate(memes):
            text = f"{i + start}. " + "/".join(meme.keywords)
            if not status:
                text = f"[color=lightgrey]{text}[/color]"
            texts.append(text)
        return "\n".join(texts)

    head_text = (
        "表情包制作\n"
        "触发方式：关键词 + 图片/文字\n"
        "可使用 “自己”、“@某人” 获取指定用户的头像作为图片，如：“摸 自己”\n"
        "发送 “表情详情 + 关键词” 可查看表情需要的参数及表情预览\n"
        "目前支持的表情列表："
    )
    head = Text2Image.from_text(head_text, 30, weight="bold").to_image(padding=(40, 20))
    imgs: List[IMG] = []
    col_num = 4
    num_per_col = math.ceil(len(meme_list) / col_num)
    for idx in range(0, len(meme_list), num_per_col):
        text = cmd_text(meme_list[idx : idx + num_per_col], start=idx + 1)
        imgs.append(Text2Image.from_bbcode_text(text, 30).to_image(padding=(40, 20)))
    w = max(sum((img.width for img in imgs)), head.width)
    h = head.height + max((img.height for img in imgs))
    frame = BuildImage.new("RGBA", (w, h), "white")
    frame.paste(head, alpha=True)
    current_w = 0
    for img in imgs:
        frame.paste(img, (current_w, head.height), alpha=True)
        current_w += img.width
    return frame.save_jpg()


if memes_config.memes_check_resources_on_startup:
    from meme_generator.download import check_resources
    from nonebot import get_driver

    driver = get_driver()

    @driver.on_startup
    async def _():
        logger.info("正在检查资源文件...")
        asyncio.create_task(check_resources())
