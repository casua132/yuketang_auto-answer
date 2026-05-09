# 雨课堂自动答题

支持大模型调用，雨课堂所有类型题目的自动作答

## 示例

<img width="1080" height="2354" alt="Weixin Image_20260509094235_4_9" src="https://github.com/user-attachments/assets/3fa58a70-76dc-4e07-809d-9305ea117d9d" />

## 特点

- **自定义时间**: 可以自定义回答时间，防止过早或过晚答题。
- **大模型调用**：使用先进大模型，高效高准确率解决非题库题目，以及图文关联的难题。
- **使用简单**: 配置完成后只须点击监听即可开始运行。

## 运行

此处为基于源代码构建apk的方法：

1.  ```bash
    git clone https://github.com/casua132/yuketang_auto-answer.git
    cd yuketang_auto-answer
    python -m venv myenv
    source myenv/bin/activate
    pip install -r requirements.txt
    ```

2.  本项目基于flet, 首先下载:
    ```bash
    pip install flet
    ```
3.  Run the build command:
    ```bash
    flet build apk --project android_app
    ```
    (注意：本项目需要 Flutter 环境 (目前，3.41.2 Flutter 版本已通过)，运行此命令会在终端提示下载flutter,请允许。详情请参阅 Flet 文档。).
    (构建过程中可能会由于网络问题出现构建失败，可以科学上网后下载，或者自行进入flutter官网下载对应版本）

## 配置

本项目目前支持豆包大模型(火山引擎每个新用户有很多免费token, 课程不多的话基本一分钱不用花）(若更倾向其他大模型，请进入Scripts/Classes.py, 修改最后一个函数的提示词以及大模型调用方法，如果可以，请创建新的函数并提交修改，帮助本项目支持更多的模型厂家服务)

首先进入火山引擎，注册账号，并开启该项目使用的模型的服务(当前为doubao-seed-1-6-vision-250815,若期望更先进的模型，只需要在Scripts/Classes.py中修改'model'变量为对应模型的名称即可)，然后下载应用并打开后，进入配置，填入api,即可完成api配置。然后点击登录，会弹出二维码，请使用第二个手机扫码，或截图后分屏，保证软件没有进入后台，然后打开微信扫描登录，当出现："已登录：xxx"说明登录成功。

## 使用说明

当有课程开课，进入软件，点击监听即可启动自动答题。该应用会自动保持屏幕常亮，但是如果熄屏或进入后台就会断联(目前并没有找到解决方法，如果有欢迎提交更改), 推荐使用备用机或分屏使用。

(注意：对于动态二维码签到课程，需要完成签到后才能使用本项目）

## 参考

- 本项目基于[TrickyDeath/RainClassroomAssitant](https://github.com/TrickyDeath/RainClassroomAssitant)开发, 增加对新版雨课堂的支持与移动端的适配。

## 声明

- 本项目仅供学习和研究使用，开发者不对使用本脚本引起的任何后果负责。
