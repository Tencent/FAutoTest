# 初始化失败问题如何调试

1. 先尝试执行adb shell am force-stop com.tencent.mm命令杀掉微信进程,然后进入待测页面重试。

2. 如果仍然失败。H5页面进入http://localhost:9222/json

   小程序页面进入http://localhost:9223/json

   查看是否成功建立连接。

   - 成功建立连接应该见到类似如图的信息：

     - <img src='https://github.com/Tencent/FAutoTest/blob/master/docs/images/connectSuc.png?raw=true' width='300'/>

3. 如果未建立连接成功，请尝试手动建立连接：

   - H5:
     - 先执行adb shell ps | grep com.tencent.mm:tools，获取到进程的pid，
     - 再执行adb forward tcp:9222 localabstract:webview_devtools_remote_%s，来执行端口映射。（将%s替换为前一步获取的pid）
     - 进入http://localhost:9222/json 查看是否连接正常。
   - 小程序：
     - 先执行adb shell dumpsys activity top | grep ACTIVITY，获取到进程的pid，
     - 再执行adb forward tcp:9223 localabstract:webview_devtools_remote_%s，来执行端口映射。（将%s替换为前一步获取的pid）
     - 进入http://localhost:9223/json 查看是否连接正常。
     - 对于部分机型小程序无法正常连接(在**chrome:inspect**中也没有小程序页面显示)，见QA。

4. 如果手动能够成功建立连接，可以查看**h5WebSocketDebugUrlFetcher**（建立H5连接）、**wxWebSocketDebugUrlFetcher**（建立小程序连接）这两个类，判断是否是机型环境不同导致的连接问题，如果存在不同机型建立连接方式不同，欢迎提出pr。

