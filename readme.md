#radioitScript

日本动画广播提取和辅助下载的python脚本。

##支持

1. hibiki.py -> [響 - HiBiKi Radio Station -](http://hibiki-radio.jp/)
1. onsen.py-> [インターネットラジオステーション＜音泉＞](http://www.onsen.ag/)
1. animate.py -> [ウェブラジオ - アニメイトTV](http://animate.tv/radio/)
1. _radioit_script_template.py，腳本模板

##例子

![t1](../../raw/master/ver1-1.png)

![t2](../../raw/master/ver1-2.png)

###`-h`, `--help`

显示帮助

###`--debug`

调试模式

###子命令 `list`

列出广播站上的广播信息，广播种类根据参数而定

####`-a`, `--all`

所有广播

####`-n`, `--new`

新广播

####`--today`

当天的广播

####`-d day`, `--day day`

本星期某日的广播，day取值1～7

###子命令 `download`

下载某个广播的资源

####`-a`, `--audio`

下载广播最新一期的音频

####`-i`, `--image`

下载广播最新一期的图片

###`-p`, `--proxy`

>有些广播站没有IP限制则此参数无效

设置代理，突破广播音频的日本IP限制。

-p socks 127.0.0.1:1080，使用socks代理，本地端点127.0.0.1:1080

-p http 127.0.0.1:1080，使用http代理，本地端点127.0.0.1:1080

####`-e`, `--everything`

下载广播最新一期的音频和图片

####`id`

广播id

###子命令 `show`

显示某广播的信息，内容根据参数选择输出

####`-n`, `--name`

名字

####`-d`, `--description`

描述

####`-t`, `--title`

最新一期的标题

####`-c`, `--comment`

最新一期的评论

####`-s`, `--schedule`

更新时间表或本期更新时间

####`-p`, `--personality`

主持人

####`-g`, `--guest`

嘉宾

####`-v`, `--verbose`

详细模式，输出所有信息

####`id`

广播id