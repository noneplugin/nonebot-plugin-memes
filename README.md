# nonebot-plugin-memes

[Nonebot2](https://github.com/nonebot/nonebot2) 插件，用于表情包制作


### 使用

**以下命令需要加[命令前缀](https://v2.nonebot.dev/docs/api/config#Config-command_start) (默认为`/`)，可自行设置为空**

支持的表情包：

发送“表情包制作”显示下图的列表：

<div align="left">
  <img src="https://s2.loli.net/2022/06/14/wOLCQF8gxvm5lIc.jpg" width="500" />
</div>


#### 字体和资源

插件使用 [nonebot-plugin-imageutils](https://github.com/noneplugin/nonebot-plugin-imageutils) 插件来绘制文字，字体配置可参考该插件的说明

插件在启动时会检查并下载图片资源，初次使用时需等待资源下载完成

可以手动下载 `resources` 下的 `images` 和 `thumbs` 文件夹，放置于机器人运行目录下的 `data/memes/` 文件夹中

可以手动下载 `resources` 下 `fonts` 中的字体文件，放置于 nonebot-plugin-imageutils 定义的字体路径，默认为机器人运行目录下的 `data/fonts/` 文件夹


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
