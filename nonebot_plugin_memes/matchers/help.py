import hashlib
from datetime import datetime, timedelta, timezone
from io import BytesIO
from itertools import chain

from meme_generator import Meme
from meme_generator.utils import MemeProperties, render_meme_list
from nonebot.utils import run_sync
from nonebot_plugin_alconna import Image, Text, on_alconna
from nonebot_plugin_localstore import get_cache_dir
from nonebot_plugin_session import EventSession, SessionIdType
from pypinyin import Style, pinyin

from ..config import memes_config
from ..manager import meme_manager
from ..recorder import get_meme_generation_keys
from .utils import UserId

memes_cache_dir = get_cache_dir("nonebot_plugin_memes")

help_matcher = on_alconna(
    "表情包制作",
    aliases={"表情列表", "头像表情包", "文字表情包"},
    block=True,
    priority=11,
    use_cmd_start=True,
)


@help_matcher.handle()
async def _(user_id: UserId, session: EventSession):
    memes = meme_manager.get_memes()
    list_image_config = memes_config.memes_list_image_config

    sort_by = list_image_config.sort_by
    sort_reverse = list_image_config.sort_reverse
    if sort_by == "key":
        memes = sorted(memes, key=lambda meme: meme.key, reverse=sort_reverse)
    elif sort_by == "keywords":
        memes = sorted(
            memes,
            key=lambda meme: "".join(
                chain.from_iterable(pinyin(meme.keywords[0], style=Style.TONE3))
            ),
            reverse=sort_reverse,
        )
    elif sort_by == "date_created":
        memes = sorted(memes, key=lambda meme: meme.date_created, reverse=sort_reverse)
    elif sort_by == "date_modified":
        memes = sorted(memes, key=lambda meme: meme.date_modified, reverse=sort_reverse)

    label_new_timedelta = list_image_config.label_new_timedelta
    label_hot_threshold = list_image_config.label_hot_threshold
    label_hot_days = list_image_config.label_hot_days

    meme_generation_keys = await get_meme_generation_keys(
        session,
        SessionIdType.GLOBAL,
        time_start=datetime.now(timezone.utc) - timedelta(days=label_hot_days),
    )

    meme_list: list[tuple[Meme, MemeProperties]] = []
    for meme in memes:
        labels = []
        if datetime.now() - meme.date_created < label_new_timedelta:
            labels.append("new")
        if meme_generation_keys.count(meme.key) >= label_hot_threshold:
            labels.append("hot")
        disabled = not meme_manager.check(user_id, meme.key)
        meme_list.append((meme, MemeProperties(disabled=disabled, labels=labels)))

    # cache rendered meme list
    meme_list_hashable = [
        (
            {
                "key": meme.key,
                "keywords": meme.keywords,
                "shortcuts": [
                    shortcut.humanized or shortcut.key for shortcut in meme.shortcuts
                ],
                "tags": sorted(meme.tags),
            },
            prop,
        )
        for meme, prop in meme_list
    ]
    meme_list_hash = hashlib.md5(str(meme_list_hashable).encode("utf8")).hexdigest()
    meme_list_cache_file = memes_cache_dir / f"{meme_list_hash}.jpg"
    if not meme_list_cache_file.exists():
        img = await run_sync(render_meme_list)(
            meme_list,
            text_template=list_image_config.text_template,
            add_category_icon=list_image_config.add_category_icon,
        )
        with open(meme_list_cache_file, "wb") as f:
            f.write(img.getvalue())
    else:
        img = BytesIO(meme_list_cache_file.read_bytes())

    msg = Text(
        "触发方式：“关键词 + 图片/文字”\n"
        "发送 “表情详情 + 关键词” 查看表情参数和预览\n"
        "目前支持的表情列表："
    ) + Image(raw=img)
    await msg.send()
