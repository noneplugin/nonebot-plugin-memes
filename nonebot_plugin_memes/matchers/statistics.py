from datetime import datetime, timedelta
from typing import Any, Optional, Union

from dateutil.relativedelta import relativedelta
from nonebot.matcher import Matcher
from nonebot_plugin_alconna import (
    Alconna,
    AlconnaQuery,
    Args,
    Option,
    Query,
    UniMessage,
    on_alconna,
    store_true,
)
from nonebot_plugin_session import EventSession, SessionIdType

from ..manager import meme_manager
from ..plot import plot_duration_counts, plot_meme_and_duration_counts
from ..recorder import get_meme_generation_records, get_meme_generation_times
from ..utils import add_timezone
from .utils import find_meme

statistics_matcher = on_alconna(
    Alconna(
        "表情调用统计",
        Args["meme_name?", str],
        Option("-g|--global", default=False, action=store_true, help_text="全局统计"),
        Option("--my", default=False, action=store_true, help_text="我的"),
        Option(
            "-t|--type",
            Args["type", ["day", "week", "month", "year", "24h", "7d", "30d", "1y"]],
            help_text="统计类型",
        ),
    ),
    aliases={"表情使用统计"},
    block=True,
    priority=11,
    use_cmd_start=True,
)


def wrapper(
    slot: Union[int, str], content: Optional[str], context: dict[str, Any]
) -> str:
    if slot == "my" and content:
        return "--my"
    elif slot == "global" and content:
        return "--global"
    elif slot == "type" and content:
        if content in ["日", "24小时", "1天"]:
            return "--type 24h"
        elif content in ["本日", "今日"]:
            return "--type day"
        elif content in ["周", "一周", "7天"]:
            return "--type 7d"
        elif content in ["本周"]:
            return "--type week"
        elif content in ["月", "30天"]:
            return "--type 30d"
        elif content in ["本月", "月度"]:
            return "--type month"
        elif content in ["年", "一年"]:
            return "--type 1y"
        elif content in ["本年", "年度"]:
            return "--type year"
    return ""


pattern_my = r"(?P<my>我的)"
pattern_type = r"(?P<type>日|24小时|1天|本日|今日|周|一周|7天|本周|月|30天|本月|月度|年|一年|本年|年度)"  # noqa E501
pattern_global = r"(?P<global>全局)"
pattern_cmd = r"表情(?:调用|使用)统计"

statistics_matcher.shortcut(
    rf"{pattern_my}{pattern_cmd}",
    prefix=True,
    wrapper=wrapper,
    arguments=["{my}"],
).shortcut(
    rf"{pattern_global}{pattern_cmd}",
    prefix=True,
    wrapper=wrapper,
    arguments=["{global}"],
).shortcut(
    rf"{pattern_my}{pattern_global}{pattern_cmd}",
    prefix=True,
    wrapper=wrapper,
    arguments=["{my}", "{global}"],
).shortcut(
    rf"{pattern_my}?{pattern_global}?{pattern_type}{pattern_cmd}",
    prefix=True,
    wrapper=wrapper,
    arguments=["{my}", "{global}", "{type}"],
)


@statistics_matcher.handle()
async def _(
    matcher: Matcher,
    session: EventSession,
    meme_name: Optional[str] = None,
    query_global: Query[bool] = AlconnaQuery("global.value", False),
    query_my: Query[bool] = AlconnaQuery("my.value", False),
    query_type: Query[str] = AlconnaQuery("type", "24h"),
):
    meme = await find_meme(matcher, meme_name) if meme_name else None

    is_my = query_my.result
    is_global = query_global.result
    type = query_type.result

    if is_my and is_global:
        id_type = SessionIdType.USER
    elif is_my:
        id_type = SessionIdType.GROUP_USER
    elif is_global:
        id_type = SessionIdType.GLOBAL
    else:
        id_type = SessionIdType.GROUP

    now = datetime.now().astimezone()
    if type == "24h":
        start = now - timedelta(days=1)
        td = timedelta(hours=1)
        fmt = "%H:%M"
        humanized = "24小时"
    elif type == "day":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        td = timedelta(hours=1)
        fmt = "%H:%M"
        humanized = "本日"
    elif type == "7d":
        start = now - timedelta(days=7)
        td = timedelta(days=1)
        fmt = "%m/%d"
        humanized = "7天"
    elif type == "week":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
            days=now.weekday()
        )
        td = timedelta(days=1)
        fmt = "%a"
        humanized = "本周"
    elif type == "30d":
        start = now - timedelta(days=30)
        td = timedelta(days=1)
        fmt = "%m/%d"
        humanized = "30天"
    elif type == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        td = timedelta(days=1)
        fmt = "%m/%d"
        humanized = "本月"
    elif type == "1y":
        start = now - relativedelta(years=1)
        td = relativedelta(months=1)
        fmt = "%y/%m"
        humanized = "一年"
    else:
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        td = relativedelta(months=1)
        fmt = "%b"
        humanized = "本年"

    if meme:
        meme_times = await get_meme_generation_times(
            session, id_type, meme_key=meme.key, time_start=start
        )
        meme_keys = [meme.key] * len(meme_times)
    else:
        meme_records = await get_meme_generation_records(
            session, id_type, time_start=start
        )
        meme_records = [
            record for record in meme_records if meme_manager.get_meme(record.meme_key)
        ]
        meme_times = [record.time for record in meme_records]
        meme_keys = [record.meme_key for record in meme_records]

    if not meme_times:
        await matcher.finish("暂时没有表情调用记录")

    meme_times = [add_timezone(time) for time in meme_times]
    meme_times.sort()

    def fmt_time(time: datetime) -> str:
        if type in ["24h", "7d", "30d", "1y"]:
            return (time + td).strftime(fmt)
        return time.strftime(fmt)

    duration_counts: dict[str, int] = {}
    stop = start + td
    count = 0
    key = fmt_time(start)
    for time in meme_times:
        while time >= stop:
            duration_counts[key] = count
            key = fmt_time(stop)
            stop += td
            count = 0
        count += 1
    duration_counts[key] = count
    while stop <= now:
        key = fmt_time(stop)
        stop += td
        duration_counts[key] = 0

    key_counts: dict[str, int] = {}
    for key in meme_keys:
        key_counts[key] = key_counts.get(key, 0) + 1
    key_counts = dict(sorted(key_counts.items(), key=lambda item: item[1]))

    if meme:
        title = (
            f"表情“{'/'.join(meme.keywords)}”{humanized}调用统计"
            f"（总调用次数为 {key_counts.get(meme.key, 0)}）"
        )
        output = await plot_duration_counts(duration_counts, title)
    else:
        title = f"{humanized}表情调用统计（总调用次数为 {sum(key_counts.values())}）"
        meme_counts: dict[str, int] = {}
        for key, count in key_counts.items():
            if meme := meme_manager.get_meme(key):
                meme_counts["/".join(meme.keywords)] = count
        output = await plot_meme_and_duration_counts(
            meme_counts, duration_counts, title
        )
    await UniMessage.image(raw=output).send()
