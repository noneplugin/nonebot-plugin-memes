<div align="center">

  <a href="https://v2.nonebot.dev/">
    <img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot">
  </a>

# nonebot-plugin-memes

_✨ [Nonebot2](https://github.com/nonebot/nonebot2) 插件，用于文字类表情包制作 ✨_

<p align="center">
  <img src="https://img.shields.io/github/license/noneplugin/nonebot-plugin-memes" alt="license">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/nonebot-2.0.0b4+-red.svg" alt="NoneBot">
  <a href="https://pypi.org/project/nonebot-plugin-memes">
    <img src="https://badgen.net/pypi/v/nonebot-plugin-memes" alt="pypi">
  </a>
  <a href="https://jq.qq.com/?_wv=1027&k=wDVNrMdr">
    <img src="https://img.shields.io/badge/QQ%E7%BE%A4-682145034-orange" alt="qq group">
  </a>
</p>

</div>


头像相关表情包制作：[nonebot-plugin-petpet](https://github.com/noneplugin/nonebot-plugin-petpet)


### ！！！注意

- 为避免表情开关的命令与“头像表情包”插件冲突，同时更准确地描述插件功能，本插件由“表情包制作”更名为“文字表情包”，相应的指令也做了调整

- 为避免误触发，大多数表情改为需要在指令后加空格，如：“鲁迅说 我没说过这句话”


### 安装

- 使用 nb-cli

```
nb plugin install nonebot_plugin_memes
```

- 使用 pip

```
pip install nonebot_plugin_memes
```

#### 字体和资源

插件使用 [nonebot-plugin-imageutils](https://github.com/noneplugin/nonebot-plugin-imageutils) 插件来绘制文字，字体配置可参考该插件的说明

插件在启动时会检查并下载图片资源，初次使用时需等待资源下载完成

可以手动下载 `resources` 下的 `images` 和 `thumbs` 文件夹，放置于机器人运行目录下的 `data/memes/` 文件夹中

可以手动下载 `resources` 下 `fonts` 中的字体文件，放置于 nonebot-plugin-imageutils 定义的字体路径，默认为机器人运行目录下的 `data/fonts/` 文件夹


### 配置项

> 以下配置项可在 `.env.*` 文件中设置，具体参考 [NoneBot 配置方式](https://v2.nonebot.dev/docs/tutorial/configuration#%E9%85%8D%E7%BD%AE%E6%96%B9%E5%BC%8F)

#### `memes_command_start`
 - 类型：`List[str]`
 - 默认：`[""]`
 - 说明：命令起始标记，默认包含空字符串

#### `memes_resource_url`
 - 类型：`str`
 - 默认：`https://ghproxy.com/https://raw.githubusercontent.com/noneplugin/nonebot-plugin-memes/v0.3.x/resources`
 - 说明：资源下载链接，默认为使用`ghproxy`代理的github仓库链接

#### `memes_disabled_list`
 - 类型：`List[str]`
 - 默认：`[]`
 - 说明：禁用的表情包列表，需填写表情名称的列表，表情名称可以在`data_source.py`文件中查看。若只是临时关闭，可以用下文中的“表情包开关”


### 使用

**以下命令需要加[命令前缀](https://v2.nonebot.dev/docs/api/config#Config-command_start) (默认为`/`)，可自行设置为空**

支持的表情包：

发送“文字表情包”显示下图的列表：

<div align="left">
  <img src="https://s2.loli.net/2022/11/29/496PAMb25GgTuyq.jpg" width="500" />
</div>


#### 表情包开关

群主 / 管理员 / 超级用户 可以启用或禁用某些表情包

发送 `启用文字表情/禁用文字表情 [表情名]`，如：`禁用文字表情 鲁迅说`

超级用户 可以设置某个表情包的管控模式（黑名单/白名单）

发送 `全局启用文字表情 [表情名]` 可将表情设为黑名单模式；

发送 `全局禁用文字表情 [表情名]` 可将表情设为白名单模式；


### 示例

 - `/鲁迅说 我没说过这句话`

<div align="left">
  <img src="https://s2.loli.net/2022/06/12/dqRF8egWb3U6Vfz.png" width="250" />
</div>


 - `/举牌 aya大佬带带我`

<div align="left">
  <img src="https://s2.loli.net/2022/06/12/FPuBosEgM3Qh1rJ.jpg" width="250" />
</div>


### 特别感谢

- [Ailitonia/omega-miya](https://github.com/Ailitonia/omega-miya) 基于nonebot2的qq机器人

- [HibiKier/zhenxun_bot](https://github.com/HibiKier/zhenxun_bot) 基于 Nonebot2 和 go-cqhttp 开发，以 postgresql 作为数据库，非常可爱的绪山真寻bot

- [kexue-z/nonebot-plugin-nokia](https://github.com/kexue-z/nonebot-plugin-nokia) 诺基亚手机图生成
