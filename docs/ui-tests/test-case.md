测试模块
用例编号
前置条件
具体测试步骤
预期结果


cocowa聊天界面测试
chat-001
1.已成功登录
2.已进入client
1.鼠标托至右侧聊天界面右上角三个点处并点击

1.1s内跳转到设置界面


chat-002
1.已成功登录
2.已进入设置界面
1.点击模型下拉框
1.正常展开并显示所有可选模型

chat-003
1.已成功登录
2.已进入设置界面
1.点击人格下拉框
1.正常展开并显示所有可选人格

chat-004
1.已成功登录
2.已进入设置界面
1.点击修改Prompt
1.进入Prompt修改界面，自定义修改风格

chat-005
1.已成功登录
2.已进入设置界面
1.点击查看完整提示词
1.进入提示词界面，可看到所有提示词

chat-006
1.已成功登录
2.已进入设置界面
1.点击查看trigger提示词
1.进入trigger提示词界面，可看到trigger的完整提示词

chat-007
1.已成功登录
2.已进入设置界面
1.点击确认键
1.退出设置界面，回到聊天界面
2.界面显示“保存成功”

chat-008
1.已成功登录
1.点击右侧聊天框内的左下角键盘标志
1.由聊天框切换至【单击或按住空格键开始说话】

chat-009
1.已成功登录
2.聊天框已切换至【单击或按住空格键开始说话】
1.鼠标点击/按住键盘空格键与coco对话

1.cocowa识别到用户的语音并转化为文字显示在聊天框界面
2.cocowa有正确回应

chat-010
1.已成功登录
2.聊天框已切换至【单击或按住空格键开始说话】
1.鼠标单击/按住键盘空格键时
1.聊天框由【单击或按住空格键开始说话】变为【松开或再次点击停止 】

chat-011
1.已成功登录
2.聊天框已切换至【单击或按住空格键开始说话】
1.再次点击右侧聊天框内左下角按钮
1.聊天框由【单击或按住空格键开始说话】变为打字输入框

chat-012
1.已成功登录
2.已进入client
1.点击聊天框右侧回形针标志
1.正确打开电脑本地文件

chat-013
1.已成功登录
2.已进入client
3.已打开本地电脑文件
1.执行完chat-012

1.上传视频/音频/图片到聊天框，cocowa能读取到对应的内容作出回应

chat-014
1.已成功登录
2.已进入client
1.点击聊天框，输入数字/字母/汉字/下划线/特殊字符/空格

1.正常输入到对话框

chat-015
1.已成功登录
2.已进入client
1.点击聊天框右侧发送键
2.点击键盘enter键
1.内容正确发送至对话框

chat-016
1.已成功登录
2.已进入client
1.当聊天框内内容为空时点击enter
2.当聊天框内内容为空时点击右侧发送键
1.点击enter键界面无反应
2.点击发送键页面显示【Empty message】

chat-017
1.已成功登录
2.已进入client
1.鼠标处于聊天框内且有上下文时，上下滚动鼠标或拖住右侧滚动条上下拉动
1.界面能正确去到上/下侧聊天记录

chat-018
1.已成功登录
2.已进入client
1.点击页面正上方【日程】按钮

1.正确跳转到日程界面

chat-019
1.已成功登录
2.已进入client
3.已进入日程界面
1.点击任意一天

1.对应的框会染上浅蓝色且能进行编辑


chat-020
1.已成功登录
2.已进入client
3.已进入日程界面
1.点击正下方按钮【回到今天】
1.今天的日期被染上蓝色

chat-021
1.已成功登录
2.已进入client
3.已进入日程界面
1.点击按钮【回到今天】右侧的【<】按钮
2.点击按钮【回到今天】右侧的【>】按钮
1.对应的日期会减一月，日程表也会回到上一月
2.对应的日期会加一月，日程表也会去到下一月

chat-022
1.已成功登录
2.已进入client
3.已进入日程界面
1.点击按钮【回到今天】右侧的圆形标志

1.日期和【回到今天】按钮被隐藏

chat-023
1.已成功登录
2.已进入client
3.已进入日程界面
1.点击右侧圆形标志
1.被隐藏的日期和按钮再次展开

chat-024
1.已成功登录
2.已进入client
3.cocowa摄像头功能正常运行
1.测试人员出现在cocowa面前
1.左下角识别框出现Unkonw单词

chat-025
1.已成功登录
2.已进入client
3.cocowa摄像头功能正常运行
4.测试人员已注册
1.测试人员出现在cocowa面前

1.左下角识别框内出现对应人员注册时的名字


chat-026
1.已成功登录
2.已进入client
1.正常使用状态
1.左下角状态栏显示normal

chat-027
1.已成功登录
2.已进入client
1.静置cocowa十分钟不操作
1.左下角状态栏显示sleep


chat-028
1.已成功登录
2.已进入client
1.语音唤醒后静置十分钟
1.状态栏显示standby

chat-029
1.已成功登录
2.已进入client
1.点击【任务】按钮
1.进入任务栏界面

chat-030
1.已成功登录
2.已进入client
1.未曾创建过任何任务

1.界面显示暂无数据

chat-031
1.已成功登录
2.已进入client
1.在聊天内创建任务例如‘下午两点提醒我喝水’
2.查看任务界面
1.界面出现新任务，新任务与创建任务一致

chat-032
1.已成功登录
2.已进入client
3.已创建一条任务
1.点击出现的任务
2.观察界面反应

1s内跳转到编辑任务界面

chat-033
1.已成功登录
2.已进入client
3.已创建一条任务
1.点击标题框对标题进行增加/修改/删除
2.点击保存
1.提示“编辑成功”

chat-034
1.已成功登录
2.已进入client
3.已创建一条任务
4.已进入编辑任务界面
1.点击下侧<task>进行修改
2.点击保存

1.页面显示编辑成功，任务体也成功修改


chat-035
1.已成功登录
2.已进入client
3.已创建一条任务
1.点击任务左侧【启用】按钮
2.等到预定时间观察coco反应
1.任务被禁用，不会被触发

chat-036

1.已成功登录
2.已进入client
3.已创建一条任务
1.点击任务左侧【禁用】按钮
2.等到预定时间观察coco反应

1.任务被启动，会触发

chat-037
1.已成功登录
2.已进入client
3.已创建一条任务
1.点击任务右侧的【删除】按钮
2.等到预定时间观察coco反应
1.任务被永久删除，不再触发

chat-038
1.已成功登录
2.已进入client
1.点击【技能】按钮
2.观察界面跳转情况
1.进入到技能界面

chat-039
1.已成功登录
2.已进入client
1.点击【Coco】按钮
2.观察界面跳转情况
1.跳转到coco固有技能界面

chat-040
1.已成功登录
2.已进入client
3.已进入技能界面
1.点击【自定义】按钮
2.观察界面跳转情况

1.跳转到cocowa自定义组合技界面

chat-041
1.已成功登录
2.已进入client
1.在聊天框中输入“坐下，站起，扇扇子命名为体能训练”
2.点击发送
1.自定义界面出现新的组合技

chat-042
1.已成功登录
2.已进入client
3.已创建一条组合技
1.鼠标拖到新的技能上，点击禁用
2.客户端输入“来个体能训练”

1.页面显示编辑成功
2.技能未被触发

chat-043
1.已成功登录
2.已进入client
3.已创建一条组合技且已被禁用
1.鼠标拖到新的技能上，点击启用
2.客户端输入“来个体能训练”
3.观察cocowa动作
1.页面显示编辑成功
2.cocowa按照预先设计的动作按顺序做出“坐下、站起、扇扇子”动作

chat-043
1.已成功登录
2.已进入client
3.已创建一条组合技
1.鼠标拖到新的技能上，点击【运行】按钮
2.查看coco动作执行情况
1.cocowa做出对应的动作，且按正确顺序完成

chat-044
1.已成功登录
2.已进入client
3.已创建一条组合技
1.鼠标拖到新的技能上，点击【删除】按钮
2.在聊天框输入“来个体能训练”
1.技能从前端消失
2.无法被触发

chat-045
1.已成功登录
2.已进入client
1.点击【话题】按钮
2.查看界面跳转情况
1.跳转到历史话题界面


chat-046
1.已成功登录
2.已进入client
3.无历史话题
1.观察历史话题变化
1.话题界面为空

chat-047
1.已成功登录
2.已进入client
1.点击【新建话题+】按钮
2.观察界面变化
1.界面显示“新建话题”
2.右侧出现空白对话框

chat-048
1.已成功登录
2.已进入client
3.当前已有话题
1.点击【新建话题+】按钮
2.观察界面变化
1.【新建话题+】按钮正下方的历史中增加新的历史话题

chat-049
1.已成功登录
2.已进入client
3.当前已有两个话题
1.依此点击历史话题
2.观察界面变化情况
1.点击历史话题对应的话题标题会加黑
2.点击后查看到对应话题的聊天记录


chat-050
1.已成功登录
2.已进入client
3.已有历史话题存在
1.鼠标拖到历史话题上，点击右侧的【...】按钮
2.点击删除
1.话题被删除，从前端消除

chat-051
1.已成功登录
2.已进入client
1.点击左上角【记忆】按钮
2.观察页面变化情况
1.跳转到cocowa记忆界面


chat-052
1.已成功登录
2.已进入client
1.点击任意日记/周记/月记/人格等时间
2.观察界面变化
1.对应的cocowa聊天记忆被打开

chat-053
1.已成功登录
2.已进入client
1.鼠标拖到右上方的用户头像处
2.点击【Cocowa studio】按钮
3.观察界面跳转情况
1.进入到Cocowa studio界面


chat-054
1.已成功登录
2.已进入client
1.点击左上角【leapwatt】按钮
2.观察界面变化

1.跳转回首页


Cocowa studio界面测试

chat-055
1.已进入CoCoWa Studio界面

1.点击【Home】按钮
2.观察界面跳转情况
1.进入到首页

chat-056
1.已进入CoCoWa Studio界面
2.已进入Home界面
1.鼠标拖动到话筒上长按讲话，讲完松手
2.按住键盘上空格键讲话，讲完松手
1.输入框由“Type a message”变为“Listening”
cocowa接收到语音信息并给予反馈

chat-057
1.已进入CoCoWa Studio界面
2.已进入Home界面
1.点击【Type a message..】
2.输入字母/下划线/中文
3.点击【send】按钮
1.发送成功
2.对应的文字出现在对话框

chat-058
1.已进入CoCoWa Studio界面
2.已进入Home界面
1.点击【Type a message..】
2.输入讲个故事
3.点击【send】右侧的闪电按钮

1.cocowa开始讲故事
2.故事被打断


chat-059
1.已进入CoCoWa Studio界面
1.点击左侧【Resource】下拉框
2.观察界面变化
1.展示出【Files】、【Prompt】按钮


chat-060
1.已进入CoCoWa Studio界面
2.已点开【Resource】下拉框
1.点击【files】按钮
2.观察界面变化
1.展示出初始文件【audios】、【code】、【document】、【image】、【video】

chat-061
1.已进入CoCoWa Studio界面
2.已进入Files界面
1.点击右上角搜索框，输入已存在的文件名
2.点击enter
1.快速筛选出同名文件


chat-062
1.已进入CoCoWa Studio界面
2.已进入Files界面
1.点击右上角【Upload】按钮
1.弹出Upload Files界面

chat-063
1.已进入CoCoWa Studio界面
2.已进入Files界面
3.已进入Upload Files界面
1.点击云标志弹出电脑本地文件供选择，选择图片/视频
2.点击【confirm】按钮

1.选中的图片/视频成功上传到files中


chat-064
1.已进入CoCoWa Studio界面
2.已进入Files界面
1.单击文件/视频/图片
2.点击【删除】按钮

1.对应的文件/视频/图片从files中消失

chat-065
1.已进入CoCoWa Studio界面
2.已进入Files界面
1.点击右上角【+Folder】按钮
2.在输入框中输入中文/英文/特殊字符/下划线
3.点击creat
1.files中出现对应名称的文件

chat-066
1.已进入CoCoWa Studio界面
2.已进入Flies界面

1.鼠标拖动到任意文件
2.点击文件右上角的【Rename】按钮，输入新的名字
3.点击【Rename】按钮
1.页面显示“Rename successfully”提示
2.文件名变为新编辑的名称


chat-067
1.已进入CoCoWa Studio界面
2.已进入Flies界面
1.点击右上角‘板子’按钮
2.观察页面布局变化
1.界面排序由横列变为纵列

chat-068
1.已进入CoCoWa Studio界面
2.已进入Files界面
1.点击右上角‘四方块’按钮
2.查看页面布局变化
1.界面排序由纵列变为横列

chat-069
1.已进入CoCoWa Studio界面
2.已点开Resource界面
1.点击【Prompt】
2.观察界面变化
1.正确弹出Prompt Viewer界面

chat-070
1.已进入CoCoWa Studio界面
2.已点开Resource界面
1.鼠标拖到四板块中的任意板块，点击【View Content】按钮
2.查看页面跳转情况
1.正确弹出Trigger System Prompt界面

chat-071
1.已进入CoCoWa Studio界面
2.已进入Trigger System Prompt界面
1.点击右上角的【x】按钮/右下角的【close】按钮
2.观察界面变化
1.回到Prompt Viewer界面


chat-072
1.已进入CoCoWa Studio界面
1.点击左侧【Resource】按钮
2.观察界面变化
1.【files】和【Prompt】按钮被隐藏

chat-073
1.已进入CoCoWa Studio界面
1.点击左侧【Development】按钮
2.观察页面跳转情况

1.正确弹出development界面

chat-074
1.已进入CoCoWa Studio界面
2.已进入Development界面
1.点击Trigger框的【Develop My Trigger】按钮
2.观察页面跳转情况
1.正确弹出Trigger Studio界面

chat-075
1.已进入CoCoWa Studio界面
2.已进入Development界面
1.点击Routine框的【Develop My Routine】按钮
2.观察页面跳转情况
1.正确弹出Routine界面

chat-076
1.已进入CoCoWa Studio界面
2.已进入Development界面
1.点击Shell框的【Develop My Shell】
2.观察页面跳转情况
1.正确弹出Shell界面

chat-077
1.已进入CoCoWa Studio界面
2.已进入Development界面
1.点击Motion框的【Develop My Motion】
2.观察页面跳转情况

1.正确弹出Motion界面

chat-078
1.已进入CoCoWa Studio界面
1.点击左侧【State】下拉框
2.观察页面变化
1.展示出【Monitor】、【Setting】按钮

chat-079
1.已进入CoCoWa Studio界面
2.已点开state下拉框
1.点击【Monitor】按钮
2.观察界面跳转情况
1.跳转到Monitor界面
2.查看到关于cocowa更多的详细信息

chat-080
1.已进入CoCoWa Studio界面
2.已点开state下拉框
1.点击【Setting】按钮
2.观察页面跳转情况
1.跳转到Setting界面

chat-081
1.已进入CoCoWa Studio界面
2.已进入Setting界面
1.点击【Language】右侧下拉框选择需要的语言
2.点击【Remote Model】右侧下拉框选择需要的模型
3.点击【Voice】右侧下拉框选择需要的声音
4.点击【Save Changes】按钮
1.展示可选择语言
2.展示可选择模型
3.展示可选择声音
4.修改被保存

chat-082
1.已进入CoCoWa Studio界面
2.已进入Setting界面
3.cocowa处于normal状态
1.点击【Standby】按钮
2.观察界面和Cocowa机身动作与灯光变化


1.页面提示‘Device switched to standby mode’
2.机身由站立状态变为折叠状态
3.灯光由浅蓝色呼吸灯变为绿色呼吸灯

chat-083
1.已进入CoCoWa Studio界面
2.已进入Setting界面
3.cocowa处于standby状态
1.点击【Sleep】按钮
2.观察界面和cocowa机身动作与灯光变化

1.页面提示‘Device switched to sleep mode’
2.机身保持折叠状态
3.灯光保持绿色呼吸灯

chat-084
1.已进入CoCoWa Studio界面
2.已进入Setting界面
3.cocowa处于sleep状态
1.点击【normal】按钮
2.观察界面和cocowa机身动作与灯光变化
1.页面提示‘Device switched to normal mode’
2.身体由折叠状态变为正常站姿
3.绿色呼吸灯变为浅蓝色呼吸灯

chat-085
1.已进入CoCoWa Studio界面
2.已进入Setting界面
3.人脸跟随功能正常工作
1.点击Face Recognition右侧按钮
2.观察cocowa的人脸跟随情况

1.左右走动cocowa头部不会再跟随

chat-086
1.已进入CoCoWa Studio界面
2.已进入Setting界面
3.yolo功能正常工作
1.点击YOLO Objection Detection右侧按钮
2.客户端输入“拍个照片描述一下面前的景象”
3.观察cocowa的回应
1.cocowa无法回应描述眼前的景象

chat-087
1.已进入CoCoWa Studio界面
2.已进入Setting界面
3.Gesture Control功能正常工作
1.点击Gesture Control右侧按钮
2.客户端输入“当时别到拳头手势就坐下”
3.在cocowa面前摆出拳头手势保持3s
4.观察cocowa身体动作变化

1.客户端任务栏中多出一条任务
2.摆出拳头手势，cocowa机身无反应


chat-088
1.已进入CoCoWa Studio界面
2.已点开State界面
1.点击【State】下拉框按钮
2.观察界面变化
1.【Monintor】、【Setting】按钮被隐藏

chat-089
1.已进入CoCoWa Studio界面
1.点击左侧【Terminal】按钮
2.观察界面跳转情况
1.弹出终端界面

chat-090
1.已进入CoCoWa Studio界面
1.点击左下侧双横一箭头按钮
2.观察页面变化情况
1.左侧栏被隐藏只显示对应菜单栏的图标

chat-091
1.已进入CoCoWa Studio界面
1.点击左下侧双横一箭头按钮
1.被隐藏的左侧栏完全显示


chat-092
1.已进入CoCoWa Studio界面
1.点击左侧【Reboot】按钮
1.前端弹出提示‘Are you sure you want to restart the device?‘

chat-093
1.已进入CoCoWa Studio界面
1.点击左侧【Reboot】按钮
2.点击确认
3.观察cocowa主机盒变化
1.cocowa主机盒重启


chat-094
1.已进入CoCoWa Studio界面
1.点击左下角【Shut Down】按钮
2.点击确认
3.观察cocowa主机盒变化
1.主机盒关机黑屏








cocowa单脚动作测试
knee-001
1.已成功登录
2.已进入client
1.客户端输入“抬起左前脚”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa抬起左前脚
2.机身保持平稳无跌倒风险
3.生成正确的xml<joint joint="left_front_paws" angle="30" speed_str="medium" / >

knee-002
1.已成功登录
2.已进入client
1.客户端输入“抬起右前脚”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa抬起右前脚
2.机身保持平稳无跌倒风险
3.生成正确的xml<joint joint="right_front_paw" angle="30" speed_str="medium" / >

knee-003
1.已成功登录
2.已进入client
1.客户端输入“抬起左后脚”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa抬起左后脚
2.机身保持平稳无跌倒风险
3.生成正确的xml<joint joint="left_rear_paws" angle="30" speed_str="medium" / >

knee-004
1.已成功登录
2.已进入client
1.客户端输入“抬起右后脚”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa抬起右后脚
2.机身保持平稳无跌倒风险
3.生成正确的xml<joint joint="right_rear_paws" angle="30" speed_str="medium" / >





cocowa单腿动作测试
thigh-001
1.已成功登录
2.已进入client
1.客户端输入“晃晃左前腿”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa正确晃动左前腿
2.机身保持平稳无跌倒风险
3.生成正确的xml

thigh-002
1.已成功登录
2.已进入client
1.客户端输入“晃晃右前腿”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa正确晃动右前腿
2.机身保持平稳无跌倒风险
3.生成正确的xml

thigh-003
1.已成功登录
2.已进入client
1.客户端输入“晃晃左后腿”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa正确晃动左后腿
2.机身保持平稳无跌倒风险
3.生成正确的xml

thigh-004
1.已成功登录
2.已进入client
1.客户端输入“晃晃右后腿”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa正确晃动右后腿
2.机身保持平稳无跌倒风险
3.生成正确的xml





cocowa耳朵动作测试
ear-001
1.已成功登录
2.已进入client
1.客户端输入“摇摇左耳”
2.观察cocowa耳朵动作
3.观察客户端xml生成
1.左耳匀速摇动
2.生成正确的xml<ear_action action="left_ear_wave" duration="5" count="2" speed_str="medium" / >

ear-002
1.已成功登录
2.已进入client
1.客户端输入“摇摇右耳”
2.观察cocowa耳朵动作
3.观察客户端xml生成
1.右耳匀速摇动
2.生成正确的xml<ear_action action="right_ear_wave" duration="5" count="2" speed_str="medium" / >

ear-003
1.已成功登录
2.已进入client
1.客户端输入“摇摇耳朵”
2.观察cocowa耳朵动作
3.观察客户端xml生成
1.双耳同步摇动
2.生成正确的xml<ear_action action="both_ears_same" duration="5" count="2" speed_str="medium" / >

ear-004
1.已成功登录
2.已进入client
1.客户端输入“异步摇耳朵”
2.观察cocowa耳朵动作
3.观察客户端xml生成
1.左右耳异步摇晃
2.生成正确的xml<ear_action action="both_ears_opposite" duration="5" count="3" speed_str="medium" / >






cocowa基础移动与姿态测试
move-001
1.已成功登录
2.已进入client
1.客户端输入“往前走”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa往前走
2.生成正确的xml <move height_str="normal" gait="walk" direction="forward" speed_str="medium" type="distance" value="20" / >

move-002
1.已成功登录
2.已进入client
1.客户端输入“往后退”
2.观察cocowa机身动作
3.观察客户端xml生成
1.ocowa后退
2.生成正确的xml<move height_str="normal" gait="walk" direction="backward" speed_str="medium" type="distance" value="20" / >

move-003
1.已成功登录
2.已进入client
1.客户端输入“往右走”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa往右走
2.生成正确的xml<move height_str="normal" gait="walk" direction="right" speed_str="medium" type="distance" value="20" / >

move-004
1.已成功登录
2.已进入client
1.客户端输入往左走
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa往左走
2.生成正确的xml<move height_str="normal" gait="walk" direction="left" speed_str="medium" type="distance" value="20" / >


cocowa动作测试


motion-001
1.已成功登录
2.已进入client
1.客户端输入“做两个俯卧撑”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa做出两个俯卧撑动
2.生成正确的xml<body_action action="push_up" duration="5" count="2" speed_str="medium" / >

motion-002
1.已成功登录
2.已进入client
1.客户端输入“来三次摇屁股”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa做出三次摇屁股动作
2.生成正确的xml<body_action action="shake_body" duration="5" count="3" speed_str="medium" / >

motion-003
1.已成功登录
2.已进入client
1.客户端输入“向前/后/左/右蠕动三次”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa做出对应方向的蠕动动作且蠕动三次
2.生成正确的xml <crawl direction="forward/backward/left/right" speed_str="medium" count="3" / >

motion-004
1.已成功登录
2.已进入client
1.客户端输入“来一次波浪动作”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa做出波浪动作
2.生成正确的xml<body_action action="dizzy_sway" count="1" speed_str="medium" / >

motion-005
1.已成功登录
2.已进入client
1.客户端输入“来一个扩胸运动”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa做一次扩胸运动动作
2.生成正确xml <body_action action="chest_expansion" count="1" speed_str="medium" / >

motion-006
1.已成功登录
2.已进入client
1.客户端输入“丁字坐”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa做出丁字坐动作
2.生成正确的xml<posture action="t_sit" / >


motion-007
1.已成功登录
2.已进入client
1.客户端输入“来个快速狗狗摇”
2.观察cocowa机身动作
3.观察客户端xml生成
1.coocwa做出狗狗摇动作
2.生成正确的xml<body_action action="dog_shake" duration="5" count="1" speed_str="fast" / >

motion-008
1.已成功登录
2.已进入client
1.客户端输入“来个匍匐前进”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa做出匍匐前进动作
2.生成正确的xml<crawl direction="forward" speed_str="medium" count="3" / >

motion-009
1.已成功登录
2.已进入client
1.客户端输入“手臂拉扯”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa做出手臂拉扯动作
2.生成正确的xml<body_action action="arm_pull_forward" duration="5" count="1" speed_str="medium" / >

motion-010
1.已成功登录
2.已进入client
1.客户端输入“苍蝇搓手”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa做出苍蝇搓手动作
2.生成正确的xml <body_action action="rub" duration="5" count="1" speed_str="medium" / >

motion-011
1.已成功登录
2.已进入client
1.客户端输入“脚扣地板”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa使用右前脚扣地板
2.生成正确的xml<body_action action="single_leg_tap" duration="5" count="1" speed_str="medium" / >

motion-012
1.已成功登录
2.已进入client
1.客户端输入“手臂敲击”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa做出右前手臂敲击地板动作
2.生成正确的xml<body_action action="tap" duration="3" count="1" speed_str="medium" / >

motion-013
1.已成功登录
2.已进入client
1.客户但输入“顺时针转圈”
2.客户但输入“逆时针转圈”
3.观察cocowa机身转圈方向
4.观察客户端xml生成
1.cocowa机身顺时针转一圈并生成xml <rotate direction="right" height_str="normal" speed_str="medium" amplitude_str="large" type="angle" value="360" / >
2.cocowa机身逆时针转一圈并生成xml <rotate direction="left" height_str="normal" speed_str="medium" amplitude_str="large" type="angle" value="360" / >

motion-014
1.已成功登录
2.已进入client
1.客户端输入“来个左右摇晃”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa做出左右摇晃动作
2.生成正确的xml<body_action action="shake_body" duration="5" count="2" speed_str="medium" / >

motion-015
1.已成功登录
2.已进入client
1.客户端输入“大跨步往前走”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa做出大跨步往前走动作
2生成正确的xml<move height_str="normal" gait="big_stride" direction="forward" speed_str="medium" type="distance" value="30" / >

motion-016
1.已成功登录
2.已进入client
1.客户端输入“小狗坐”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa做出小狗坐动作
2.生成正确的xml<posture action="dog_sit" / >

motion-017
1.已成功登录
2.已进入client
1.客户端输入“坐下（默认正常坐）”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa按标准正常坐坐下
2.生成正确的xml<posture action="sit" / >

motion-018
1.已成功登录
2.已进入client
1.客户端输入“站起（默认标准站立）”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa做出标准站立动作
2.生成正确的xml<posture action="stand" / >

motion-019
1.已成功登录
2.已进入client
1.客户端输入“向左倾斜”
2.客户端输入“向右倾斜”
3.观察cocowa机身动作
4.观察客户端xml生成
1.cocowa做出向左倾斜动作并生成xml <posture action="lean_left" / >
2.cocowa做出向右倾斜动作并生成xml <posture action="lean_right" / >

motion-020
1.已成功登录
2.已进入client
1.客户端输入“眩晕”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa做出眩晕的动作
2.生成正确的xml<body_action action="dizzy_sway" count="1" speed_str="medium" / >

motion-021
1.已成功登录
2.已进入client
1.客户端输入“摔倒”
2.观察cocowa机身动作
3.观察客户端xml生成
1.cocowa做出“摔倒”动作
2.生成正确的xml <posture action="fallen" / >

具体动作请参考需求文档动作专项优化






cocowa组合技测试


Combination Skill-001
1.已成功登录
2.已进入client
1.客户端输入“把坐下、站起、折叠、展开、往前跑、往后退记为名为体能训练的组合技”
2.查看客户端中技能栏下的自定义栏
1.客户端生成正确组合技


Combination Skill-002
1.已成功登录
2.已进入client
3.已进入客户端中技能栏下得自定义栏
1.点击组合技的运行
2.观察页面提示
3.观察cocowa机身动作
1.页面提示指令已发送
2.cocowa按照组合技预定顺序展示动作

Combination Skill-003
1.已成功登录
2.已进入client
3.已进入客户端中技能栏下得自定义栏
1.点击编辑，将坐下xml改为扩胸运动
2.点击保存
3.观察界面提示
4.点击运行
1.提示改成功
2.且点击运行后原先的坐下动作被替换为扩胸运动

Combination Skill-004
1.已成功登录
2.已进入client
1.客户端输入“体能训练”
2.点击发送
3.观察cocowa机身动作
1.cocowa按照组合技预定顺序展示动作

Combination Skill-005
1.已成功登录
2.已进入client
3.已进入客户端技能栏下得自定义栏
1.鼠标滑倒组合技区域点击删除
2.观察界面变化
3.客户端输入“体能训练”
1.组合技从客户端消失
2.输入后cocowa会根据自己的理解展示动作但不是预先设置的











cocowa表情测试


具体表情展示请参考需求文档

face-001
1.已成功登录
2.已进入client
1.客户端输入“眼神跟随”
2.查看cocowa表情变化
3.查看客户端xml生成
1.cocowa展示出眼神跟随表情
2.生成正确的xml<face_emo emo="Face_Track" duration="3" / >

face-002
1.已成功登录
2.已进入client
1.客户端输入“微微开心”
2.查看cocowa表情变化
3.查看客户端xml生成
1.cocowa展示出微微开心表情
2.生成正确的xml<face_emo emo="smile" / >

face-003
1.已成功登录
2.已进入client
1.客户端输入“很开心”
2.查看cocowa表情变化
3.查看客户端xml生成
1.cocowa展示出很开心表情
2.生成正确的xml<face_emo emo="Very_Happy" / >

face-004
1.已成功登录
2.已进入client
1.客户端输入“超级开心”
2.查看cocowa表情变化
3.查看客户端xml生成
1.cocowa展示出超级开心表情
2.生成正确的xml<face_emo emo="Super_Happy" / >

face-005
1.已成功登录
2.已进入client
1.客户端输入“思考”
2.查看cocowa表情变化
3.查看客户端xml生成
1.cocowa展示出思考表情
2.生成正确的xml<face_emo emo="Thinking" / >

face-006
1.已成功登录
2.已进入client
1.客户端输入“专注”
2.查看cocowa表情变化
3.查看客户端xml生成
1.cocowa展示出专注表情
2.生成正确的xml<face_emo emo="Listening" / >

face-007
1.已成功登录
2.已进入client
1.客户端输入“困惑”
2.查看cocowa表情变化
3.查看客户端xml生成
1.cocowa展示出困惑表情
2.生成正确的xml<face_emo emo="Confused" / >


face-008

1.已成功登录
2.已进入client
1.客户端输入“愤怒”
2.查看cocowa表情变化
3.查看客户端xml生成
1.cocowa展示出愤怒表情
2.生成正确的xml<face_emo emo="Annoyed" / >

face-009
1.已成功登录
2.已进入client
1.客户端输入“尴尬”
2.查看cocowa表情变化
3.查看客户端xml生成
1.cocowa展示出尴尬表情
2.生成正确的xml<face_emo emo="Embarrassed" / >

face-010
1.已成功登录
2.已进入client
1.客户端输入“吃惊”
2.查看cocowa表情变化
3.查看客户端xml生成
1.cocowa展示出吃惊表情
2.生成正确的xml<face_emo emo="Surprised" / >

face-011
1.已成功登录
2.已进入client
1.客户端输入“嫌弃”
2.查看cocowa表情变化
3.查看客户端xml生成
1.cocowa展示出嫌弃表情
2.生成正确的xml<face_emo emo="Disgusted" / >

face-012
1.已成功登录
2.已进入client
1.客户端输入“沮丧”
2.查看cocowa表情变化
3.查看客户端xml生成
1.cocowa展示出沮丧表情
2.生成正确的xml<face_emo emo="sad" / >

face-013
1.已成功登录
2.已进入client
1.客户端输入“委屈”
2.查看cocowa表情变化
3.查看客户端xml生成
1.cocowa展示出委屈表情
2.生成正确的xml<face_emo emo="Wronged" / >

face-014
1.已成功登录
2.已进入client
1.客户端输入“顽皮”
2.查看cocowa表情变化
3.查看客户端xml变化
1.cocowa展示出顽皮表情
2.生成正确的xml<face_emo emo="Playful" / >

face-015
1.已成功登录
2.已进入client
1.客户端输入“休眠”
2.查看cocowa表情变化
3.查看客户端xml变化
1.cocowa展示出休眠表情
2.生成正确的xml<face_emo emo="Resting" / >

表情需求&验收标准 1120













cocowa音色与情绪匹配测试

voice
1.已成功登录
2.已进入client
3.喇叭功能正常
1.切换机器人所有预设音色，每种音色配合对应情绪的语音输出（如欢快音色+开心话术）
1.音色切换无卡顿，每种音色清晰可辨
2.音色与情绪匹配度高（符合产品定义），无杂音

voice-chinese-001
1.已成功登录
2.已进入client
3.喇叭功能正常
1.客户端输入“使用惊喜/难过的情绪讲出爽快思思的音色”
2.聆听cocowa讲出的声音
1.cocowa用对应的情绪讲出爽快思思的音色

voice-chinese-002
1.已成功登录
2.已进入client
3.喇叭功能正常
1.客户端输入“使用惊喜/害怕/憎恨/难过的情绪讲出柔美女友的音色”
2.聆听cocowa讲出的声音
1.cocowa用对应的情绪讲出柔美女友的音色

voice-chinese-003
1.已成功登录
2.已进入client
3.喇叭功能正常
1.客户端输入“使用害怕/难过的情绪讲出儒雅男友的音色”
2.聆听cocowa讲出的声音

1.cocowa用对应的情绪讲出儒雅男友的音色

voice-chinese-004
1.已成功登录
2.已进入client
3.喇叭功能正常
1.客户端输入“使用惊喜/憎恨的情绪讲出京腔侃爷的音色”
2.聆听cocowa讲出的声音
1.cocowa用对应的情绪讲出京腔侃爷的音色

voice-english-001
1.已成功登录
2.已进入client
3.喇叭功能正常
1.客户端输入“分别使用affectionate/angry/ASMR/chat/ excited/happy/neutral/warm/sad情绪讲出Nadia的音色”
2.聆听cocowa讲出的声音
1.cocowa用对应的情绪讲出Nadia的音色

voice-english-002
1.已成功登录
2.已进入client
3.喇叭功能正常
1.客户端输入“分别使用affectionate/angry/ASMR/chat/ excited/happy/neutral/warm/sad情绪讲出Candice的音色”
2.聆听cocowa讲出的声音
1.cocowa用对应的情绪讲出Candice的音色


voice-english-003
1已成功登录
2.已进入client
3.喇叭功能正常
1.客户端输入“分别使用affectionate/angry/ASMR/chat/ excited/happy/neutral/warm/sad/authoritative情绪讲出Corey的音色”
2.聆听cocowa讲出的声音
1.cocowa用对应的情绪讲出Corey的音色


voice-english-004
1已成功登录
2.已进入client
3.喇叭功能正常
1.客户端输入“分别使用affectionate/angry/ASMR/chat/ excited/happy/neutral/warm/sad情绪讲出Glen的音色”
2.聆听cocowa讲出的声音
1.cocowa用对应的情绪讲出Glen的音色

special voice-001
1已成功登录
2.已进入client
3.喇叭功能正常
1.客户端输入“来一段广西口音讲故事”
1.cocowa用广西口音讲一段故事

special voice-002
1已成功登录
2.已进入client
3.喇叭功能正常
1.客户端输入“使用樱桃小丸子的音色来讲故事”
1.cocowa用樱桃小丸子的音色讲故事

special voice-003
1已成功登录
2.已进入client
3.喇叭功能正常
1.客户端输入“使用懒洋洋的音色讲故事”
1.cocowa用懒洋洋的音色讲故事

special voice-004
1已成功登录
2.已进入client
3.喇叭功能正常
1.客户端输入“使用海绵宝宝的音色讲故事”
1.cocowa用海绵宝宝的音色讲故事



cocowa拍照功能测试

capture-001
1.已成功登录
2.已进入client
3.摄像头功能正常
1.客户端输入“看看前方有什么”

1.cocowa在三秒返回一张正前方景色的照片
2.对照片中的景象进行正确描述

capture-002
1.已成功登录
2.已进入client
3.摄像头功能正常
1.客户端输入“看看左边有什么”
1.cocowa按照先转头再拍照顺序拍照
2.返回左边的景象并进行正确的描述


capture-003
1.已成功登录
2.已进入client
3.摄像头功能正常
1.客户端输入“看看右边有什么”
1.cocowa按照先转头再拍照顺序正确拍照
2.返回右边的照片并对照片景象进行描述

capture-004
1.已成功登录
2.已进入client
3.摄像头功能正常
1.客户端输入“看看后边有什么”
1.cocowa按照先转身体再拍照顺序正确拍照
2.返回后方的照片并对照片景象进行描述

capture-005
1.已成功登录
2.已进入client
3.摄像头功能正常
1.客户端输入“看看上边有什么”
1.cocowa按照先抬头再拍照顺序正确拍照
2.返回上方景象的照片并进行描述

capture-006
1.已成功登录
2.已进入client
3.摄像头功能正常
1.客户端输入“看看下面有什么”
1.cocowa按照先低头再拍照顺序正确拍照
2.返回下方景象的照片并进行描述



Cocowa led灯功能测试
head-light-001
1.已成功登录
2.已进入client
3.led灯功能正常
1.刚开机正常交互状态
1.正常模式，四肢正常站立
2.灯光为浅蓝色闪烁

head-light-002
1.已成功登录
2.已进入client
3.led灯功能正常
1.客户端输入进入休眠模式或十分钟不操作
2.观察cocowa动作
3.观察cocowa灯光变化
1.进入休眠模式，四肢自动折叠
2.灯光变为深蓝色闪烁


head-light-003
1.已成功登录
2.已进入client
3.led灯功能正常
1.客户端输入待机模式
2.观察cocowa动作
3.观察cocowa灯光变化
1.进入待机模式，四肢折叠
2.灯光变为绿色闪烁

body-light-001
1.已成功登录
2.已进入client
3.led灯功能正常
1.连接type-c
2.观察灯光变化

1.充电状态，灯光为绿色闪烁

body-light-002
1.已成功登录
2.已进入client
3.led灯功能正常
1.不接电源正常使用状态
2.观察灯光变化

1.灯光为蓝色闪烁

body-light-003
1.已成功登录
2.已进入client
3.led灯功能正常
1.持续使用至电量低于20%
2.观察灯光变化
1.灯光为红色闪烁












cocowa手势识别







Gesture Recognition-001
1.已成功登录
2.已进入client
3.摄像头功能正常
1.在cocowa面前摆出1手势
2.观察前端手势识别模块

1.cocowa在一秒内识别到并在前端手势识别模块展示出“one”

Gesture Recognition-002
1.已成功登录
2.已进入client
3.摄像头功能正常
1.在cocowa面前摆出2手势
2.观察前端手势识别模块
1.cocowa在一秒内识别到并在前端手势识别模块展示出“two”

Gesture Recognition-003
1.已成功登录
2.已进入client
3.摄像头功能正常
1.在cocowa面前摆出3手势
2.观察前端手势识别模块
1.cocowa在一秒内识别到并在前端手势识别模块展示出“three”

Gesture Recognition-004
1.已成功登录
2.已进入client
3.摄像头功能正常
1.在cocowa面前摆出4手势
2.观察前端手势识别模块
1.cocowa在一秒内识别到并在前端手势识别模块展示出“four”

Gesture Recognition-005
1.已成功登录
2.已进入client
3.摄像头功能正常
1.在cocowa面前摆出5手势
1.cocowa在一秒内识别到并在前端手势识别模块展示出“five”

Gesture Recognition-006
1.已成功登录
2.已进入client
3.摄像头功能正常
1.在cocowa面前摆出6手势
1.cocowa在一秒内识别到并在前端手势识别模块展示出“six”

Gesture Recognition-007
1.已成功登录
2.已进入client
3.摄像头功能正常
1.在cocowa面前摆出拳头手势
1.cocowa在一秒内识别到并在前端手势识别模块展示出“fist”

Gesture Recognition-008
1.已成功登录
2.已进入client
3.摄像头功能正常
1.在cocowa面前摆出rock手势
1.cocowa在一秒内识别到并在前端手势识别模块展示出“rock”

Gesture Recognition-009
1.已成功登录
2.已进入client
3.摄像头功能正常
1.在cocowa面前摆出鄙视手势
1.cocowa在一秒内识别到并在前端手势识别模块展示出“middleFinger”

具体手势参考需求文档手势识别方案优化



cocowa Trigger测试

trigger-001
1.已成功登录
2.已进入client
3.摄像头功能正常
1.客户端输入“当你识别到1手势就坐下”
2.在cocowa面前摆出1手势
1.在任务界面出现一条新的任务
2.cocowa识别到手势1坐下

trigger-002
1.已成功登录
2.已进入client
3.摄像头功能正常
1.客户端输入“当你识别到rock手势就站起”
2.在cocowa面前摆出rock手势
1.在任务界面出现一条新的任务
2.cocowa识别到rock手势立刻站起


trigger-003
1.已成功登录
2.已进入client
3.摄像头功能正常
1.客户端输入“这周五下午两点提醒我看牙医”

1.在任务界面出现一条新的任务
2.cocowa到了设定时间自动触发Trigger提醒用户看牙医
