#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
import os
import sys
import time

from PIL import Image, ImageDraw, ImageFont

from logic.Image import DebugImage, EPDImage, AbstractImage
from libs.lib.waveshare_epd import epd4in2bc

logging.basicConfig(level=logging.DEBUG)

# python3 Main.py debug
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

    picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'libs/pic')
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

    blackImage = Image.new('1', (epd.width, epd.height), 255)  # 298*126
    redImage = Image.new('1', (epd.width, epd.height), 255)  # 298*126  ryimage: red or yellow image

    drawBlack = ImageDraw.Draw(blackImage)
    drawRed = ImageDraw.Draw(redImage)

    if debugMode:
        drawRed = drawBlack

    image.text((10, 0), 'Jenkins Build Status', font=font24, fill=AbstractImage.BLACK)
    image.line((5, 30, 395, 30), fill=AbstractImage.BLACK)

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
