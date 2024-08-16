from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_alconna")
require("nonebot_plugin_waiter")
require("nonebot_plugin_session")
require("nonebot_plugin_userinfo")
require("nonebot_plugin_localstore")
require("nonebot_plugin_session_orm")

from . import matchers, migrations  # noqa
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="表情包制作",
    description="制作各种沙雕表情包",
    usage=(
        "- 表情列表\n"
        "发送 “表情包制作” 查看表情列表\n"
        "- 表情详情\n"
        "发送 “表情详情 + 表情名/关键词” 查看表情详细信息和表情预览\n"
        "- 表情搜索\n"
        "发送 “表情搜索 + 关键词” 查找相关的表情\n"
        "- 表情包开关\n"
        "- “超级用户” 和 “管理员” 可以启用或禁用某些表情包\n"
        "发送 启用表情/禁用表情 表情名/关键词，如：禁用表情 摸\n"
        "- “超级用户” 可以设置某个表情包的管控模式（黑名单/白名单）\n"
        "发送 全局启用表情 表情名/关键词 可将表情设为黑名单模式；\n"
        "发送 全局禁用表情 表情名/关键词 可将表情设为白名单模式；"
    ),
    type="application",
    homepage="https://github.com/noneplugin/nonebot-plugin-memes",
    config=Config,
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna",
        "nonebot_plugin_session",
        "nonebot_plugin_userinfo",
    ),
    extra={"orm_version_location": migrations},
)
