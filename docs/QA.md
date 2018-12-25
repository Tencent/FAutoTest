## Q&A

1. pip安装过程中，一直出现timeout，安装失败 
> - 请设置是否设置代理，若设置了请检查代理设置是否正确，若仍无法解决，可手动下载无法安装的库，然后进行本地安装 

2. pip安装过程中，出现Command “python setup.py egg_info failed with error code 1” 
> - 安装pip install setuptools_scm ; 安装 pip install pytest-runner 

3. 小程序框架初始化一直报错 

> * 有可能在开启小程序之前开启过别的小程序。需要使用adb shell am force-stop com.tencent.mm命令杀掉微信进程 
> * 详情见[调试指引](https://github.com/Tencent/FAutoTest/blob/master/docs/INITERROR.md)

4. 封装的UIAutomator无法正常使用，一直报告prc错误

> * 因为手机环境问题，UIAutomator没有正常安装，执行命令： 
>
> * ```
>   adb shell pm uninstall com.github.uiautomator
>   adb shell pm uninstall com.github.uiautomator.test
>   adb install app-uiautomator.apk
>   adb install app-uiautomator-test.apk
>   adb push bundle.jar /data/local/tmp/
>   adb push uiautomator-stub.jar /data/local/tmp/
>   ```
>
>   详情可见 [uiautomator]([*https://github.com/xiaocong/uiautomator/issues/172*](https://github.com/xiaocong/uiautomator/issues/172) )

5. 拖拽等操作怎么进行

> 通过getElementCoordinateByXpath获得坐标。然后调用driver.d.drag() UIAutomator的方法来进行操作。 

6. 如果body中有多个跨域的Iframe怎么办

> 调用getAllContext、getAllIFrameNode、getBodyNode方法，通过返回值来获取需要的contextId以及NodeId
> [Iframe操作指引](IFRAME.md)

7. 为什么部分机型小程序无法进入debug模式(在**chrome:inspect**中也没有小程序页面显示)

> 最新版本微信会根据机型来使用不同的浏览器内核。如果没有使用QQ浏览器X5内核，则无法进入调试模式。
> 可以安装提供的6.6.3版本的微信，通过微信降级来解决。
> [6.6.3版本微信下载](assert/weixin663android1260.apk)
> 降级微信后，需要重新开启微信debug模式，见[开启微信debug模式](DEBUG.md)

8. 小程序无法输入文字

> 请检查手机，设置-》输入法 中，WxInput输入法插件是否启用，如果未勾选启用，请手动勾选。