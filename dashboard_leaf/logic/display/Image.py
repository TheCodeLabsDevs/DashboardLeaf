import abc
from abc import ABC

from PIL import Image, ImageDraw


class AbstractImage(ABC):
    BLACK = 0
    RED = 1

    @abc.abstractmethod
    def text(self, position, text, font, fill):
        pass

    @abc.abstractmethod
    def line(self, frame, fill):
        pass

    @abc.abstractmethod
    def rectangle(self, frame, outline, fill):
        pass

    @abc.abstractmethod
    def get_black_image(self):
        pass

    @abc.abstractmethod
    def get_red_image(self):
        pass


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
