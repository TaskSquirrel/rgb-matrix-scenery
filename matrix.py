from datetime import datetime
import sys
import signal
import time
import threading
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

def create_font():
    font = graphics.Font()
    font.LoadFont('./fonts/7x13.bdf')

    return font

def widths(font, characters):
    w = {}

    for c in characters:
       w[c] = font.CharacterWidth(ord(c))

    return w

def string_width(s, widths):
    return sum(widths[c] for c in s)

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def native(self):
        return graphics.Color(self.r, self.g, self.b)

class MatrixBase:
    def __init__(self, rows, cols, refresh_rate = 20):
        self.rows = rows
        self.cols = cols
        self.refresh_rate = refresh_rate

        options = RGBMatrixOptions()
        options.rows = rows
        options.cols = cols
        options.hardware_mapping = 'adafruit-hat'

        self.options = options
        self.matrix = RGBMatrix(options = options)
        self.font = create_font()
        self.widths = widths(self.font, '$!@#%^*()[]0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-=+_. ')

        self.frame = self.matrix.CreateFrameCanvas()

    def flush(self):
        self.frame = self.matrix.SwapOnVSync(self.frame)

    def new_frame(self):
        return StockMatrixFrame(self)

    def clear(self):
        self.frame.Clear()

    def stop(self):
        self.matrix.Clear()

class MatrixThreader(threading.Thread):
    def __init__(self, base, scene):
        threading.Thread.__init__(self)

        self._base = base
        self._scene = scene

    def run(self):
        frames_since_start = 0
        relative_frames = 0

        while True:
            objects_to_draw = []

            base = self._base
            base.clear()

            should_continue = self._scene.load(objects_to_draw, frames_since_start, relative_frames)

            for obj in objects_to_draw:
                obj._render(base)

            base.flush()

            time.sleep(1 / base.refresh_rate)

            frames_since_start = frames_since_start + 1
            relative_frames = relative_frames + 1 if should_continue else 0

        self._base.stop()

