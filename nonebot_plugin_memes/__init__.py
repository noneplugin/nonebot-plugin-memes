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
    usage="发送“表情包制作”查看表情包列表",
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
