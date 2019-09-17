#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib/pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib/lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd4in2bc
import time
from PIL import Image, ImageDraw, ImageFont

import sys


class AbstractImage:

    BLACK = 0
    RED = 1

    def text(self, position, text, font, fill):
        raise NotImplementedError

    def line(self, frame, fill):
        raise NotImplementedError

    def rectangle(self, frame, outline, fill):
        raise NotImplementedError

    def get_black_image(self):
        raise NotImplementedError

    def get_red_image(self):
        raise NotImplementedError


class EPDImage(AbstractImage):

    def __init__(self, width, height):
        self.__blackImage = Image.new('1', (width, height), 255)
        self.__redImage = Image.new('1', (width, height), 255)

        self.__drawBlack = ImageDraw.Draw(self.__blackImage)
        self.__drawRed = ImageDraw.Draw(self.__redImage)

    def text(self, position, text, font, fill):
        if fill == AbstractImage.BLACK:
            self.__drawBlack.text(position, text, font=font, fill=0)
        else:
            self.__drawRed.text(position, text, font=font, fill=0)

    def line(self, frame, fill):
        if fill == AbstractImage.BLACK:
            self.__drawBlack.line(frame, fill=0)
        else:
            self.__drawRed.line(frame, fill=0)

    def rectangle(self, frame, outline, fill):
        if fill == AbstractImage.BLACK:
            self.__drawBlack.rectangle(frame, outline=outline, fill=0)
        else:
            self.__drawRed.rectangle(frame, outline=outline, fill=0)

    def get_black_image(self):
        return self.__blackImage

    def get_red_image(self):
        return self.__redImage


class DebugImage(AbstractImage):

    def __init__(self, width, height):
        self.__image = Image.new('RGB', (width, height), (255, 255, 255))
        self.__draw = ImageDraw.Draw(self.__image)

    def text(self, position, text, font, fill):
        if fill == AbstractImage.BLACK:
            self.__draw.text(position, text, font=font, fill=(0, 0, 0))
        else:
            self.__draw.text(position, text, font=font, fill=(255, 0, 0))

    def line(self, frame, fill):
        if fill == AbstractImage.BLACK:
            self.__draw.line(frame, fill=(0, 0, 0))
        else:
            self.__draw.line(frame, fill=(255, 0, 0))

    def rectangle(self, frame, outline, fill):
        if fill == AbstractImage.BLACK:
            self.__draw.rectangle(frame, outline=outline, fill=(0, 0, 0))
        else:
            self.__draw.rectangle(frame, outline=outline, fill=(255, 0, 0))

    def get_black_image(self):
        return self.__image

    def get_red_image(self):
        return self.__image


logging.basicConfig(level=logging.DEBUG)

# python3 test.py debug
debugMode = sys.argv[1] == "debug" if len(sys.argv) == 2 else False

if debugMode:
    logging.warning("Running in debug mode")

try:
    epd = epd4in2bc.EPD()
    image = DebugImage(epd.width, epd.height)
    if not debugMode:
        logging.info("init and Clear")
        epd.init()
        epd.Clear()
        time.sleep(1)

        image = EPDImage(epd.width, epd.height)

    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

    blackImage = Image.new('1', (epd.width, epd.height), 255)  # 298*126
    redImage = Image.new('1', (epd.width, epd.height), 255)  # 298*126  ryimage: red or yellow image

    drawBlack = ImageDraw.Draw(blackImage)
    drawRed = ImageDraw.Draw(redImage)

    if debugMode:
        drawRed = drawBlack

    image.text((10, 0), 'Jenkins Build Status', font=font24, fill=AbstractImage.BLACK)
    image.line((20, 50, 70, 100), fill=AbstractImage.BLACK)
    image.line((70, 50, 20, 100), fill=AbstractImage.BLACK)
    image.rectangle((20, 50, 70, 100), outline=0, fill=AbstractImage.BLACK)
    image.line((165, 50, 165, 100), fill=AbstractImage.RED)
    image.line((140, 75, 190, 75), fill=AbstractImage.RED)
    image.rectangle((80, 50, 130, 100), outline=0, fill=AbstractImage.RED)
    if debugMode:
        image.get_black_image().save("img.png")
    else:
        epd.display(epd.getbuffer(image.get_black_image()), epd.getbuffer(image.get_red_image()))

    time.sleep(2)

    logging.info("Goto Sleep...")
    if not debugMode:
        epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd4in2bc.epdconfig.module_exit()
    exit()
