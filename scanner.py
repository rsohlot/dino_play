from PIL import Image
from datetime import datetime
import os
import pyautogui
import threading
from PIL import ImageGrab
import win32gui
import pykeyboard
import sys
dino_color = (83, 83, 83)#, 255)

def screenshot(x, y, w, h):
    
    toplist, winlist = [] ,[]
    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
    win32gui.EnumWindows(enum_cb, toplist)

    chrome = [(hwnd, title) for hwnd, title in winlist if 'chrome' in title.lower()]
    # just grab the hwnd for first window matching chrome
    chrome = chrome[0]
    hwnd = chrome[0]
    
    win32gui.SetForegroundWindow(hwnd)
    bbox = win32gui.GetWindowRect(hwnd)
    img = ImageGrab.grab(bbox=(x,y,w,h))
    img.save('tmp.PNG')
    #img.show()
    return img

def is_dino_color(pixel):
    return pixel == dino_color

def obstacle(distance, length, speed, time):
    return { 'distance': distance, 'length': length, 'speed': speed, 'time': time }

class Scanner:
    def __init__(self):
        self.dino_start = (0, 0)
        self.dino_end = (0, 0)
        self.last_obstacle = {}
        self.__current_fitness =    0
        self.__change_fitness = False

    def find_game(self):
        image = screenshot(0, 0, 1500, 1500)
        size = image.size
        pixels = []
        for y in range(0, size[1], 10):
            for x in range(0, size[0], 10):
                color = image.getpixel((x, y))
                if is_dino_color(color):
                    pixels.append((x, y))

        if not pixels:
            raise Exception("Game not found!")

        self.__find_dino(pixels)

    def __find_dino(self, pixels):
        start = pixels[0]
        end = pixels[1]
        for pixel in pixels:
            if pixel[0] < start[0] and pixel[1] > start[1]:
                start = pixel
            if pixel[0] > end[0] and pixel[1] > end[1]:
                end = pixel
        self.dino_start = start
        self.dino_end = end

    def find_next_obstacle(self):
        image = screenshot(450, 170, 778, 285)
        dist = self.__next_obstacle_dist(image)
        if dist < 50 and not self.__change_fitness:
            self.__current_fitness += 1
            self.__change_fitness = True
        elif dist > 50:
            self.__change_fitness = False
        time = datetime.now()
        delta_dist = 0
        speed = 0
        if self.last_obstacle:
            delta_dist = self.last_obstacle['distance'] - dist
            speed = (delta_dist / ((time - self.last_obstacle['time']).microseconds)) * 10000
        self.last_obstacle = obstacle(dist, 1, speed, time)
        return self.last_obstacle

    def __next_obstacle_dist(self, image):
        s = 0
        for y in range(0, 115, 5):
            for x in range(0, 328, 5):
                color = image.getpixel((x, y))
                if is_dino_color(color):
                    s += 1
        if s > 50:
            raise Exception('Game over!')

        for x in range(0,328, 5):
            for y in range(0, 115, 5):
                color = image.getpixel((x, y))
                if is_dino_color(color):
                    return x
        return 1000000

    def reset(self):
        self.last_obstacle = {}
        self.__current_fitness = 0
        self.__change_fitness = False

    def get_fitness(self):
        return self.__current_fitness

