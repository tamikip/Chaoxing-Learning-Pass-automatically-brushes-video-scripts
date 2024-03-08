import cv2
import numpy as np
import time
import pyautogui
import pytesseract
from PIL import Image
from pynput import keyboard
import threading
import os
import re

num = 0
quit_time = 0

pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR/tesseract.exe'

pyautogui.FAILSAFE = True


class KeyMonitor(threading.Thread):
    def __init__(self):
        super().__init__()
        self._running = True

    def run(self):
        with keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release
        ) as listener:
            listener.join()

    def on_press(self, key):
        try:
            if key == keyboard.Key.f2:
                print('检测到按下F2键，系统结束')
                os._exit(0)
                # 在这里可以添加其他的处理逻辑
        except AttributeError:
            pass

    def on_release(self, key):
        if self._running:
            self._running = False
            # 停止监听器
            return False


def is_valid_format(input_str):
    pattern = r'^\d{2}:\d{2}$'
    if re.match(pattern, input_str):
        return True
    else:
        return False


def time_to_seconds(time):
    minutes, seconds = map(int, time.split(':'))
    return minutes * 60 + seconds


key_monitor = KeyMonitor()
key_monitor.start()
answer = input("选择学习通端，客户端输入1，网页端输入2(输入其他默认2)")
if answer == "1":
    is_web = False
    print("已选择客户端")
else:
    is_web = True
    print("已选择网页端")
input("默认开启2倍速，请先手动把速度调为2倍，否则程序会出错。（回复ok后开始）")
answer = input("播放时长选择（1.自动模式，自动获取视频时长，但是可能出错）（2.手动模式，手动填写视频时长，尽量填长一点）")
if answer == "1":
    auto_time = True
    print("已选择自动模式，如果出错，请选择手动模式。")
else:
    auto_time= False
    print("已选择手动模式")
    while True:
        try:
            time_second = int(input("请填写视频时长（”最长视频的时长“）单位秒"))
            break
        except:
            print("请填写整数数字！")
            continue

print("程序将在三秒后运行...按下F2可以立刻终止程序。")
time.sleep(3)
print("程序已启动！")
while True:
    quit_time = 0
    print("开始扫描标记点...")
    screenshot = pyautogui.screenshot()
    screenshot.save('looking.png')
    # 读取图片
    image = cv2.imread('looking.png')

    # 将颜色空间从 BGR 转换到 HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 定义在 HSV 空间中的橙色范围
    lower_orange = np.array([10, 100, 100])
    upper_orange = np.array([25, 255, 255])

    # 创建一个掩膜，只包含定义的橙色范围
    mask = cv2.inRange(hsv, lower_orange, upper_orange)

    # 应用掩膜到原始图片
    result = cv2.bitwise_and(image, image, mask=mask)

    # 寻找掩膜中的轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 初始化一个列表来存储坐标
    coordinates = []

    filtered_coordinates = [coord for coord in coordinates if coord[0] > 1750 and coord[1] < 2000]

    merged_coordinates = []
    for coord in filtered_coordinates:
        if not merged_coordinates or coord[1] != merged_coordinates[-1][1] - 1:
            merged_coordinates.append(coord)
        else:
            # 如果当前坐标的y值大于上一个坐标的y值，则替换
            if coord[1] > merged_coordinates[-1][1]:
                merged_coordinates[-1] = coord

    merged_coordinates = merged_coordinates[::-1]
    print("标记点的坐标:", merged_coordinates)

    print("标记点个数:", len(merged_coordinates))

    if len(merged_coordinates) != 0:
        one_site = merged_coordinates[num]
        print(one_site)
        pyautogui.moveTo(one_site[0] - 200, one_site[1])
        pyautogui.click()
        time.sleep(1)
        if not is_web:
            pyautogui.moveTo(300, 230)
        else:
            pyautogui.moveTo(190, 220)
        pyautogui.click()
        time.sleep(2)
        if not is_web:
            pyautogui.moveTo(800, 640)
        else:
            pyautogui.moveTo(742, 664)
        pyautogui.click()
        pyautogui.moveTo(100, 200, duration=2)
        if auto_time:
            pyautogui.screenshot('time.png')
            image = Image.open('time.png')
            if not is_web:
                cropped_image = image.crop((292, 900, 385, 947))
            else:
                cropped_image = image.crop((180, 960, 280, 1010))
            cropped_image.save('time.png')
            image = Image.open("time.png")
            time1 = pytesseract.image_to_string(image, lang='eng')
            times = re.findall(r'\b\d{1,2}:\d{2}\b', time1)
            try:
                times = times[1]
            except:
                print("本标记点貌似不是视频，自动跳到下一个标记点。")
                num += 1
                continue
            if not is_valid_format(times):
                print("本标记点貌似不是视频，自动跳到下一个标记点。")
                num += 1
                continue
            print("本视频时长:", times)
            seconds = time_to_seconds(times)
        else:
            seconds = time_second
        seconds = seconds * (1 / 2)
        # pyautogui.moveTo(1208, 934)
        # pyautogui.click()
        # time.sleep(0.2)
        # pyautogui.click()
        # time.sleep(0.2)
        # pyautogui.click()
        pyautogui.moveTo(0, 0)

        time.sleep(seconds + 2)
        pyautogui.moveTo(1880, 400)
        pyautogui.click()
    else:
        print("未找到标记点，自动翻页...")
        pyautogui.moveTo(1880, 640)
        pyautogui.scroll(-250)
        quit_time += 1
        if quit_time > 5:
            os._exit()
