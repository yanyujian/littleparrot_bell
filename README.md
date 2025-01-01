# Little Parrot Timer / 小虎皮鹦鹉计时器

A Pomodoro Timer application dedicated to the memory of my beloved pet parrot who passed away on December 21, 2024.

这是一个番茄钟计时器应用程序，献给我在2024年12月21日离世的挚爱宠物鹦鹉。

## About / 关于

This project is created as a memorial to my little budgerigar, a cherished companion who brought happiness and warmth to
my life. The application serves both as a practical productivity tool and a tribute to the joyful spirit of my feathered
friend.

这个项目是为了纪念我的小虎皮鹦鹉而创建的，它是我生命中带来欢乐和温暖的珍贵伙伴。这个应用程序既是一个实用的生产力工具，也是对我这位羽毛朋友欢快精神的致敬。

## Why do I create this project for my little budgerigar? / 为什么我会创建这个项目来纪念我的小虎皮鹦鹉？

2024年12月21日，由于是周六，所以把它从笼子里放出来让它自己玩。下午1点04分，小鹦鹉从摄像头中消失（飞到了书房/厨房/次卧/别的地方），紧接着从摄像头中听到它的呼救声。它的小伙伴期间来回多次盘旋，从笼子（摄像头视线内）非到事发地（未知）。1点13分，我从外面回来，因为跟家人说话，没注意到它的求救声，1点15分开始，再也听不到它的声音。2点10分发现这只小黄鹦鹉不见了，后续翻遍了可能的地方（书房的书全部翻出来了），未能找到。
我总觉得应该做点什么，纪念这只可爱的小精灵。想来想去，还是做个跟时间相关的程序吧。
加上之前看过一些番茄工作法的书，做个小工具纪念它吧。

On December 21, 2024, since it was a Saturday, we let it out of its cage to play on its own. At 1:04 PM, the little
parrot disappeared from the camera’s view (it flew to the study/kitchen/guest room/other places). Shortly afterward,
cries for help could be heard from the camera. Its little companion flew back and forth several times, from the cage (
within the camera's view) to the scene of the incident (location unknown).

At 1:13 PM, I returned home but, preoccupied with talking to family, didn’t notice its cries for help. By 1:15 PM, its
voice could no longer be heard. At 2:10 PM, I discovered that the little yellow parrot was missing. Despite searching
every possible location (even flipping through all the books in the study), it couldn’t be found.

I feel like I should do something to commemorate this adorable little spirit. After much thought, I’ve decided to create
a time-related program to honor it. Having read some books about the Pomodoro Technique, I thought I could make a small
tool in its memory.

### 2024-12-25 23：11:11  目前双语的功能还有点bug，功能性都可用了，后续我会慢慢迭代。

December 25, 2024, 11:11 PM – The bilingual functionality still has some bugs at the moment, but the tool is functional.
I’ll gradually improve it in future updates.

**祝所有的小精灵快乐、健康。**
**Wishing all little spirits happiness and good health.**

## Features / 功能特点

- Customizable Pomodoro timer / 可自定义的番茄钟计时器
- Project-based task tracking / 基于项目的任务跟踪
- Statistics visualization / 统计数据可视化
- System tray integration / 系统托盘集成
- Adjustable opacity and always-on-top options / 可调节透明度和窗口置顶选项
- Elegant and minimal interface / 优雅简约的界面
- Multi-language support (English/Chinese) / 多语言支持（英文/中文）

## Technical Details / 技术细节

Built with / 使用技术:

- Python
- PyQt5
- SQLite
- xlsxwriter

## Installation / 安装方法

1. Clone the repository / 克隆仓库
   ```bash
   git clone https://github.com/yanyujian/littleparrot_bell.git
   ```

2. Install requirements / 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application / 运行应用
   ```bash
   python main.py
   ```
4. You can just download the release version and run the exe file / 直接下载release版本，运行exe文件 .

## Usage / 使用说明

- Right-click the system tray icon to access all features / 右键点击系统托盘图标访问所有功能
- Left-click and drag to move the timer window / 左键点击并拖动来移动计时器窗口
- Double-click the system tray icon to show/hide the timer / 双击系统托盘图标显示/隐藏计时器
- Right-click the system tray icon and select export to export the task details into an Excel file at the program
  directory / 右键点击系统托盘图标并选择导出，将任务详情导出到程序目录下的Excel文件中

### QA

#### I want to modify the project name or delete the project, how can I do it? / 我想修改项目名称或删除项目，怎么办？

- Download sqliteBrowser at https://sqlitebrowser.org/ and open the Pomodoro.db file at the program directory. You can
  modify the project name or delete the project in the project table. / 在https:
  //sqlitebrowser.org/下载sqliteBrowser，打开程序目录下的Pomodoro.db文件，你可以在项目表中修改项目名称或删除项目。

### I want to change the language of this software,how can I do this? / 我想更改软件的语言，怎么办？

- Right-click the system tray icon,select the language you want to use.**Then restart the application.** /
  右键点击系统托盘图标，选择你想使用的语言。 **重启程序。**

## License / 许可证

This project is open source and available under the MIT License.

本项目采用 MIT 许可证开源。

## In Memory / 纪念

This project is dedicated to my little budgerigar (? - December 21, 2024).
May your spirit soar freely in the endless sky.

谨以此项目献给我的小虎皮鹦鹉（? - 2024年12月21日）。
愿你的灵魂在无垠的天际自由翱翔。

## Screenshot

就是这只可爱的小黄鹦鹉，吃个饭都要跑碗里抢吃的，如今它走了……
![Little Parrot就是这只可爱的小黄鹦鹉，吃个饭都要跑碗里抢吃的，如今它走了……](/images/littleparrot.png)

![StartPage](/images/start1.png)

![Create Project](/images/project.png)

![Set Timer](/images/timer.png)

![Settings](/images/settings.png)

![Statistics](/images/statistics.png)

## How to set the auto start / 如何设置开机自启动

Note: This program won't add itself to the startup list automatically. You need to add it manually.Auto start feature
won't be developed,because I want to keep this program clean and simple. Just like my bird. /
注意：这个程序不会自动添加到启动列表中，你需要手动添加。 开机自启动功能不会开发，因为我想保持这个程序的干净、简洁。就像我的小鹦鹉一样。

1. 找到程序文件（如littleparrot.exe) ,右键点击，选择发送到桌面快捷方式 / 1. Find the program file (e.g.,
   littleparrot.exe), right-click, and select "Create shortcut" to create a desktop shortcut.
2. 将桌面快捷方式复制到C:\Users\用户名\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup / 2. Copy the
   desktop shortcut to C:\Users\YourUsername\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup

## Update Logs

### 2024-12-28 12:59:34 确保计时结束时能够填写任务记录/ Ensure that task records can be filled out when the timer ends

1. If no project has been created, the program will prompt the user to create a project before record the task. /
   如果没有创建项目，程序会提示用户在记录任务之前创建项目。
2. Remember the last project . / 记住上次的项目。 (仅在同一次运行中有效/Only valid in the same run)

### 2024-12-28 14:00

1. 记住上次设置的时长/ Remember the last set duration

2. 14:06:13 将上次设置的项目保存到配置中，程序再启动后还能记住 。 / Save the last set project to the configuration file so
   that the program can remember it after restarting.

3. 14:12:21 设置程序图标。/ Set the program icon.

4. 14:27:59 Fix opacity bug. / 修复透明度bug。

### 2024-12-30 23:50:45

1. 按住Ctrl键，点击停止时，可以强制停止并弹出任务填写框。此功能每日限制最多使用5次。 / Hold down the Ctrl key and click stop
   to force stop and pop up the task fill box. This function can be used up to 5 times per day.
2. 按菜单调整计时时长，也计入配置文件。/ Adjust the timing duration by the menu, also recorded in the configuration file.

### 2025-01-01 19:48:14
1. 增加手动补录记录的功能（目前无法修改补录任务的完成时间，短期应该不会加）。 / Add the function of manually supplementing records (currently unable to modify the completion time of the supplementary task, it should not be added in the short term).