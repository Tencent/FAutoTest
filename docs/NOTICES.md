# 注意事项

### 1. 设备连接

当连接有多个设备时，需要先传入设备号。

H5页面：` h5Driver = H5Driver(deviceId)`

小程序：`wxDriver = WxDriver(deviceId)`

### 2. 初始化和结束框架

进入H5页面之后再调用 `initDriver()`

使用前在小程序首屏时调用`initDriver()`

在测试完成后需调用`driver.close()`方法结束框架

### 3. 环境一致性

最好在启动H5页面/小程序前先杀掉微信后台进程，保证环境一致

初始化小程序框架时，要确保微信只开启过这一个小程序;如果之前开启过其他小程序，需要使用`adb shell am force-stop com.tencent.mm`命令杀掉微信进程，再开启小程序进行测试

### 4. 控件查找

如何找到要点击的控件的xpath：通过`chrome:inspect` 找到当前页面，可以找到要点击控件的xpath（小程序一般是在当前页面的inspect的第二个）

### 5. 与Native页面组合操作

框架内部已经封装了UiAutomator来进行native的操作：可以通过`driver.d`来执行，可执行的操作与java的UiAutomator类似，具体使用方法可以见[uiautomator](*https://github.com/xiaocong/uiautomator*)