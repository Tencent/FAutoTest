# APIs

### 微信H5

* **def clickElementByXpath(self, xpath, visibleItemXpath =None, duration=50,  tapCount=1)**

> **接口说明：** 点击指定xpath的控件当控件不可见时，会自动滑动到该控件可见时，再进行点击当container为空时，默认滑动点为整个屏幕中间
>
> **参数说明：** xpath：要点击控件的xpath
>
> visibleItemXpath：当有container时，传入container中任意一个当前可见item的xpath，之后将目标滑到该可见item的位置
>
> duration:两次点击的间隔时间
>
> tapCount:点击次数 



* **def textElementByXpath(self, xpath, text)**

> **接口说明：**
>
> 先获取输入框的焦点，再使用Chrome debug协议的输入api，输入文字内容
>
> **参数说明：** xpath:输入框的xpath
>
> text:要输入的文字



* **def scrollWindow(self, x, y, xDistance, yDistance, speed=80)**

> **接口说明：**
>
> 通过坐标来滑动（屏幕的左上角为(0,0),向下和向右坐标逐渐增大）
>
> **参数说明：** x: 滑动的起始X点坐标
>
> y: 滑动的起始Y点坐标
>
> xDistance: X方向滑动的距离
>
> yDistance: Y方向滑动的距离
>
> speed: 滑动的速度



* **def getHtml(self, nodeId=1)**

> **接口说明：**
>
> 获得指定nodeId的Html代码
>
> **参数说明:**
>
> nodeId: getDocument方法返回的nodeId，当为1时，返回整个body的代码



- **def closeWindow(self)**

> **接口说明：**
>
> 获得getHtml中需要的nodeId,在调用getHtml之前必须先调用这个方法 



- **def returnLastPage(self)**

> **接口说明：**
>
> 返回上一页 



* **def scrollPickerByXpath(self, xpath)**

> **接口说明：**
>
> 滑动选择picker的选项 
>
> **参数说明：**
>
> xpath: 要选择的item 



* **def getPageHeight(self)**

>  **接口说明：**
>
> 获取整个page页面的高度



* **def getWindowHeight(self)**

> **接口说明：**
>
> 获取手机屏幕的高度 



* **def getWindowWidth(self)**

> **接口说明：**
>
> 获取手机屏幕的宽度



* **def getElementTextByXpath(self, xpath)**

> **接口说明：** 获取目标的text内容
>
> **参数说明：** xpath:目标的xpath



* **def getElementSrcByXpath(self, xpath)**

> **接口说明：** 获取目标的src内容
>
> **参数说明：** xpath:目标的xpath



* **def getElementClassNameByXpath(self, xpath)**

> **接口说明：** 获取目标的className
>
> **参数说明：** xpath:目标的xpath



* **def getCurrentPageUrl(self)**

> **接口说明：** 当前页面的url



* **def getElementByXpath(self, xpath)**

> **接口说明：** 返回lxml包装过的element对象，可以使用lxml语法获得对象的信息
>
> **参数说明：** xpath:目标的xpath
>
> 例如：可以使用element.get("attrs")来拿到属性的数据;可以用element.text拿到它的文字；当element中含有列表时，使用for循环读取每一个iteml;更多的lxml的element的操作方法可见http://lxml.de/tutorial.html



* **def isElementExist(self, xpath)**

> **接口说明：** 返回一个boolean，判断该element是否存在
>
> **参数说明：** xpath: 目标的xpath



* **def navigateToPage(self, url)**

> **接口说明：** 跳转到指定url，在微信版本6.5.13以上不可用
>
> **参数说明：** url: 要跳转的url



* **def executeScript(self, script)**

> **接口说明：** 手动发送js命令并执行，返回执行结果
>
> **参数说明：** script:要执行的js指令



* **def focusElementByXpath(self, xpath)**

> **接口说明：** 调用目标的focus()方法。
>
> **参数说明：** xpath:目标的xpath



* **def scrollToElementByXpath(self, xpath, visibleItemXpath =None, speed=400)**

> **接口说明：**
>
> 滑动屏幕，使指定xpath的控件可见默认滑动点为屏幕的中心，且边距为整个屏幕；当有container时，传入container中任意一个当前可见item的xpath，之后会将目标滑到该可见item的位置
>
> **参数说明：** xpath: 要滑动到屏幕中控件的xpath
>
> visibleItemXpath: container中当前可见的一个item的xpath；此时滑动位置是该container中间



* **def clearInputTextByXpath(self, xpath)**

> **接口说明：** 清空输入框的文字
>
> **参数说明：** xpath:input框的xpath



* **def getMemoryInfo(self)**

> **接口说明：** 获得H5进程占用内存信息



* **def getCPUInfo(self)**

> **接口说明：** 获得H5进程占用CPU信息



* **def setDebugLogMode(self)**

> **接口说明：** log信息级别调整设置，默认只显示info级别的消息
>
> 在initDriver调用后，可以调用此方法来设置显示debug级别的详细的消息

 

* **getElementCoordinateByXpath(self, elementXpath)**

> **接口说明：** 获得Element的坐标
>
> **参数说明：** param elementXpath:待获取坐标的元素的xpath
>
> **返回值：** element相对于整个屏幕的x、y坐标，单位为px

 

* **def longClickElementByXpath(self,xpath, visibleItemXpath=None, duration=2000, tapCount=1)**

> **接口说明：** 长按点击，默认时间为2s，其他同2.2.1

 

* **def repeatedClickElementByXpath(self,xpath, visibleItemXpath=None, duration=50, tapCount=2)**

> **接口说明：** 点击多次，默认双击，其他同2.2.1

 

* **getIFrameContextId(self)**

> **接口说明：** 当body标签中只有一个Iframe时调用，获得contextId

 

* **def getIFrameNodeId(self)**

> **接口说明：** 当body标签中只有一个Iframe时调用，获得nodeId

 

* **def getAllContext(self)**

> **接口说明：** 获得当前页面所有的ContextId，域以及FrameId，当有body中有多个跨域Iframe时，可以通过此方法拿到对应Iframe的FrameId



* **def getAllIFrameNode(self)**

> **接口说明：** 获得body标签中所有的IFrameNode



* **def getBodyNode(self)**

> **接口说明：** 获得body中所有node的frameId



* **def getIFrameElementCoordinateByXpath(self, elementXpath, iFrameXpath, contextId)**

> **接口说明：** 获得Element的坐标
>
> **参数说明：** param elementXpath:待获取坐标的元素的xpath
>
> iFrameXpath: 外层iFrame的xpath
>
> contextId: iFrame的ContextId
>
> **返回值：** element相对于整个屏幕的x、y坐标，单位为px



* **def getIFrameHtml(self, nodeId=None)**

> **接口说明：** 获得指定nodeId页面的Html



* **def getIFrameElementByXpath(self, xpath, nodeId)**

> **接口说明：** nodeId为element所在页面的nodeId，其余同2.2.16





## 小程序

小程序提供的接口方法与H5类似，可参考H5的接口详细说明

* **def returnLastPage(self)**

* **def getPageHeight(self)**

* **def getWindowWidth(self)**

* **def isElementExist(self, xpath)**

* **def getElementTextByXpath(self, xpath)**

* **def getElementSrcByXpath(self, xpath)**

* **def textElementByXpath(self, xpath, text, needClick=False)**

> **参数说明：** needClick: 如果为true，会先对控件进行一次点击，以获得焦点

* **def clickElementByXpath(self, xpath, containerXpath=None，byUiautomator=False)**

> **参数说明：** byUiautomator：当传统方式无法点击时，将byUiautomator传入true使用Uiautomator进行点击def getWindowHeight(self):

* **def scrollWindow(self, x, y, xDistance, yDistance, speed=800)**

* **def scrollToElementByXpath(self, xpath, containerXpath=None, speed=400)**
* **def getDocument(self)**

* **def getHtml(self, nodeId=1)**

* **def getElementByXpath(self, xpath)**

* **def getMemoryInfo(self)**

* **def getCPUInfo(self)**

* **def setDebugLogMode(self)**

* **getElementCoordinateByXpath(self, elementXpath)**