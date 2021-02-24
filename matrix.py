from datetime import datetime
import sys
import signal
import time
import threading
import multiprocessing
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

    def clear(self):
        self.frame.Clear()

    def stop(self):
        self.matrix.Clear()

class MatrixContext:
    def __init__(self):
        self.frames = 0

class MatrixTaskRunner:
    def __init__(self, context, base, tasks):
        self._context = context
        self._base = base
        self.tasks = tasks

    def on_init(self):
        for task, owner in self.tasks:
            task.container.matrix = self._base
            task.container.owner = owner
            task.container.before()

    def run(self):
        frames = self._context.frames
        refresh_rate_fps = self._base.refresh_rate
        tasks_for_current_frame = [task for task, owner in self.tasks if frames % (task.seconds * refresh_rate_fps) == 0 and (task.repeat == None or task.repeat > task._n)]

        for task_runner in tasks_for_current_frame:
            thread = threading.Thread(target = task_runner._run_task)
            thread.start()


class MatrixRunner:
    def __init__(self, base, scene):
        self._base = base
        self._scene = scene
        self._context = MatrixContext()

    def thread(self):
        return MatrixThreader(self._base, self._scene, self._context)

class MatrixThreader(threading.Thread):
    def __init__(self, base, scene, context):
        threading.Thread.__init__(self)

        self._base = base
        self._scene = scene
        self._context = context

        self._prepare()

    def _prepare(self):
        tasks = [(task, obj) for panel in self._scene._panels for obj in panel._objects for task in obj._actions]
        self._task_runner = MatrixTaskRunner(self._context, self._base, tasks)
        self._task_runner.on_init()

    def run(self):
        relative_frames = 0

        while True:
            frames_since_start = self._context.frames
            objects_to_draw = []

            base = self._base
            base.clear()

            self._task_runner.run()

            should_continue = self._scene.load(objects_to_draw, frames_since_start, relative_frames)

            for obj in objects_to_draw:
                obj._render(base)

            base.flush()

            time.sleep(1 / base.refresh_rate)

            self._context.frames = frames_since_start + 1
            relative_frames = relative_frames + 1 if should_continue else 0

        self._base.stop()

