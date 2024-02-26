<div align="center">

  <a href="https://nonebot.dev/">
    <img src="https://nonebot.dev/logo.png" width="200" height="200" alt="nonebot">
  </a>

# nonebot-plugin-memes

_✨ [Nonebot2](https://github.com/nonebot/nonebot2) 表情包制作插件 ✨_

<p align="center">
  <img src="https://img.shields.io/github/license/noneplugin/nonebot-plugin-memes" alt="license">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/nonebot-2.2.0+-red.svg" alt="NoneBot">
  <a href="https://pypi.org/project/nonebot-plugin-memes">
    <img src="https://badgen.net/pypi/v/nonebot-plugin-memes" alt="pypi">
  </a>
  <a href="https://jq.qq.com/?_wv=1027&k=wDVNrMdr">
    <img src="https://img.shields.io/badge/QQ%E7%BE%A4-682145034-orange" alt="qq group">
  </a>
</p>

</div>

> [!NOTE]
>
> 本插件 v0.4.x 以上版本为原 [头像表情包](https://github.com/noneplugin/nonebot-plugin-petpet) 与 [文字表情包](https://github.com/noneplugin/nonebot-plugin-memes/tree/v0.3.x) 整合而来，合并为 “表情包制作”
>
> 本插件负责处理聊天机器人相关逻辑，具体表情包制作相关资源文件和代码在 [表情包生成器 meme-generator](https://github.com/MeetWq/meme-generator) 中

> [!NOTE]
>
> 可使用 [nonebot-plugin-memes-api](https://github.com/noneplugin/nonebot-plugin-memes-api)（表情包制作 调用 api 版本），将 NoneBot 插件端与 `meme-generator` 分开部署
>
> `nonebot-plugin-memes-api` 与 `nonebot-plugin-memes` 功能上基本一致

### 安装

- 使用 nb-cli

```
nb plugin install nonebot_plugin_memes
```

- 使用 pip

```
pip install nonebot_plugin_memes
```

并按照 [NoneBot 加载插件](https://nonebot.dev/docs/tutorial/create-plugin#加载插件) 加载插件

#### 字体和资源

插件默认在启动时会检查 [meme-generator](https://github.com/MeetWq/meme-generator) 所需的图片资源

需按照 [meme-generator 字体安装](https://github.com/MeetWq/meme-generator/blob/main/docs/install.md#字体安装) 自行安装字体

##### 字体显示不正常解决流程

- 检查字体是否安装完整

至少需要安装一种中文字体和 Emoji 字体，部分表情需要安装额外的字体，详情请参考 [meme-generator 字体安装](https://github.com/MeetWq/meme-generator/blob/main/docs/install.md#字体安装)

- 删除 Matplotlib 字体缓存

`meme-generator` 依赖 `matplotlib` 来寻找系统字体，`matplotlib` 会生成一个缓存文件，安装新的字体之后需要删掉该文件以重新扫描字体

> 缓存文件位置：
>
> - Windows: `C:\Users\<username>\.matplotlib\fontlist-xxx.json`
> - Linux: `~/.cache/matplotlib/fontlist-xxx.json`
> - Mac: `~/Library/Caches/matplotlib/fontlist-xxx.json`

- 删除表情列表图片缓存

插件会缓存生成的表情列表图片以避免重复生成，若因为字体没安装好等原因导致生成的图片不正常，需要删除缓存的图片

缓存图片存放在 [nonebot-plugin-localstore](https://github.com/nonebot/plugin-localstore) 插件定义的缓存目录下

> 默认缓存目录位置：
>
> - Windows: `C:\Users\<username>\AppData\Local\nonebot2\Cache\nonebot_plugin_memes`
> - Linux: `~/.cache/nonebot2/nonebot_plugin_memes`
> - Mac: `~/Library/Caches/nonebot2/nonebot_plugin_memes`

### 配置项

> 以下配置项可在 `.env.*` 文件中设置，具体参考 [NoneBot 配置方式](https://nonebot.dev/docs/appendices/config)

#### `memes_command_start`

- 类型：`List[str]`
- 默认：`[]`
- 说明：命令前缀，若不配置则使用 [NoneBot 命令前缀](https://nonebot.dev/docs/appendices/config#command-start-和-command-separator)

#### `memes_command_force_whitespace`

- 类型：`bool`
- 默认：`True`
- 说明：是否强制要求命令后加空格（仅当命令后是文本时需要加空格）

#### `memes_disabled_list`

- 类型：`List[str]`
- 默认：`[]`
- 说明：禁用的表情包列表，需填写表情的`key`，可在 [meme-generator 表情列表](https://github.com/MeetWq/meme-generator/blob/main/docs/memes.md) 中查看。若只是临时关闭，可以用下文中的“表情包开关”

#### `memes_check_resources_on_startup`

- 类型：`bool`
- 默认：`True`
- 说明：是否在启动时检查 `meme-generator` 资源

#### `memes_prompt_params_error`

- 类型：`bool`
- 默认：`False`
- 说明：是否在图片/文字数量不符或参数解析错误时提示（若没有设置命令前缀不建议开启，否则极易误触发）

#### `memes_use_sender_when_no_image`

- 类型：`bool`
- 默认：`False`
- 说明：在表情需要至少1张图且没有输入图片时，是否使用发送者的头像（谨慎使用，容易误触发）

#### `memes_use_default_when_no_text`

- 类型：`bool`
- 默认：`False`
- 说明：在表情需要至少1段文字且没有输入文字时，是否使用默认文字（谨慎使用，容易误触发）

### 使用

**以下命令需要加 [NoneBot 命令前缀](https://nonebot.dev/docs/appendices/config#command-start-和-command-separator) (默认为`/`)，可自行添加空字符**

#### 表情列表

发送 “表情包制作” 查看表情列表

#### 表情帮助

- 发送 “表情详情 + 表情名/关键词” 查看 表情详细信息 和 表情预览

示例：

<div align="left">
  <img src="https://s2.loli.net/2023/03/10/1glyUrwELCHMfkT.png" width="250" />
</div>

#### 表情包开关

“超级用户” 和 “管理员” 可以启用或禁用某些表情包

发送 `启用表情/禁用表情 [表情名/表情关键词]`，如：`禁用表情 摸`

“超级用户” 可以设置某个表情包的管控模式（黑名单/白名单）

发送 `全局启用表情 [表情名/表情关键词]` 可将表情设为黑名单模式；

发送 `全局禁用表情 [表情名/表情关键词]` 可将表情设为白名单模式；

> [!NOTE]
>
> “超级用户” 可通过 [NoneBot SuperUsers](https://nonebot.dev/docs/appendices/config#superusers) 设置
>
> “管理员” 目前包括：OneBot V11 适配器中的群主、管理员

#### 表情使用

发送 “关键词 + 图片/文字” 制作表情

可使用 “自己”、“@某人” 获取指定用户的头像作为图片

可使用 “@ + 用户id” 指定任意用户获取头像，如 “摸 @114514”

可将回复中的消息作为文字和图片的输入

示例：

<div align="left">
  <img src="https://s2.loli.net/2023/03/10/UDTOuPnwk3emxv4.png" width="250" />
</div>

> [!NOTE]
>
> - 为避免误触发，当输入的 图片/文字 数量不符时，默认不会进行提示，可通过 `memes_prompt_params_error` 配置项进行设置
> - 为避免误触发，对于不需要图片输入的表情，默认需在关键词后加空格，如 “鲁迅说 我没有说过这句话”，可通过 `memes_command_force_whitespace` 配置项进行设置
> - 本插件通过 [nonebot-plugin-userinfo](https://github.com/noneplugin/nonebot-plugin-userinfo) 插件获取用户名和用户头像，具体平台支持范围可前往该插件查看
> - 本插件通过 [nonebot-plugin-alconna](https://github.com/nonebot/plugin-alconna) 来实现多适配器消息接收、获取图片输入、获取回复内容等，相关问题可前往该插件查看

#### 随机表情

发送 “随机表情 + 图片/文字” 可随机制作表情

随机范围为 图片/文字 数量符合要求的表情

### 相关插件

- [nonebot-plugin-send-anything-anywhere](https://github.com/felinae98/nonebot-plugin-send-anything-anywhere) 一个帮助处理不同 adapter 消息的适配和发送的插件
- [nonebot-plugin-alconna](https://github.com/nonebot/plugin-alconna) 强大的 Nonebot2 命令匹配拓展，支持富文本/多媒体解析，跨平台消息收发
- [nonebot-plugin-session](https://github.com/noneplugin/nonebot-plugin-session) Nonebot2 会话信息提取与会话 id 定义插件
- [nonebot-plugin-userinfo](https://github.com/noneplugin/nonebot-plugin-userinfo) Nonebot2 用户信息获取插件
