#radioScript

日本动画广播提取和辅助下载的python脚本。

##支持

1. hibiki.py -> [響 - HiBiKi Radio Station -](http://hibiki-radio.jp/)
1. onsen.py -> [インターネットラジオステーション＜音泉＞](http://www.onsen.ag/)
1. animate.py -> [ウェブラジオ - アニメイトTV](http://animate.tv/radio/)

##使用参数

###`-i`，`--image`

如果有附带的图片则下载图片

###`-a`，`--audio`

下载广播音频或者提取音频链接

###`-d`，`--description`

显示当期广播的描述

###`-c`，`--complete`

相当于同时组合`-i`、`-a`和`-d`。

###`-p`，`--proxy`

设置代理，突破广播音频的日本IP限制。

-p socks 127.0.0.1:1080，使用socks代理，本地端点127.0.0.1:1080

-p http 127.0.0.1:1080，使用http代理，本地端点127.0.0.1:1080

###`-h`，`--help`

显示帮助

##例子

![t1](1.png)

![t2](2.png)