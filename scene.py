import time
from rgbmatrix import graphics

'''
Scene lets you describe how you want to display objects onto your RGB matrix
over time using a series of `Panel`s.
'''

class MatrixObjectError(Exception):
    pass

class Modifier:
    def modify(self, obj):
        raise Error('Not implemented')

class CenterHorizontally(Modifier):
    def modify(self, obj):
        pos_x = 0.5 * (self.base.cols - string_width(text.text, self.base.widths))
        obj.x = pos_x

class RepeatableTask:
    def __init__(self, owner):
        self.owner = owner
        self.seconds = 1
        self.container = None
        self.repeat = None

        self._n = 0

    def every(self, seconds):
        self.seconds = seconds

        return self.owner

    def do(self, state_container):
        self.container = state_container

        return self.owner

    def times(self, n):
        self.repeat = n

        return self.owner

    def _run_task(self):
        self._n = self._n + 1

        self.container.update()

class MatrixObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base = None
        self._actions = []

    def every(self, seconds):
        if not seconds:
            raise MatrixObjectError('Repeat time not given')

        repeatable_task = RepeatableTask(self)
        repeatable_task.every(seconds)

        self._actions.append(repeatable_task)

        return repeatable_task

    def do(self, task):
        repeatable_task = RepeatableTask(self)
        repeatable_task.do(task)

        self._actions.append(repeatable_task)

        return repeatable_task

    def apply(self, modifier):
        modifier.base = self.base
        modifier.modify(self)

        return self

    def _render(self, matrix_base):
        '''Implementation for rendering a object onto a native canvas'''

        raise MatrixObjectError('Cannot render a plain MatrixObject')

class Text(MatrixObject):
    def __init__(self, text, color, x, y):
        super().__init__(x, y)

        self.text = text
        self.color = color
        self.last_length = None

    def _render(self, matrix_base):
        native_frame = matrix_base.frame

        self.last_length = graphics.DrawText(native_frame, matrix_base.font, self.x, self.y, self.color.native(), self.text)

class Panel:
    def __init__(self, base):
        self._base = base
        self._objects = []

        # Duration of the panel
        self._frames = 0
        self._frames_delay = 0

    def duration(self, seconds):
        self._frames = self._base.refresh_rate * seconds

    def frames(self, frames):
        self._frames = frames

    def delay(self, delay_seconds = 0):
        self._frames_delay = self._base.refresh_rate * delay_seconds

    def add(self, obj):
        if isinstance(obj, MatrixObject):
            obj.base = self._base
            self._objects.append(obj)
        else:
            raise MatrixObjectError()

    def _display(self, current_frame):
        '''Returns true if current_frame has not reached this panel's ending frame'''
        delay = self._frames_delay
        end_at = self._frames + delay

        return (current_frame >= delay and current_frame <= end_at, current_frame >= end_at)

class Scene:
    def __init__(self, base):
        self._base = base
        self._panels = []

    def create_panel(self):
        panel = Panel(self._base)
        self._panels.append(panel)

        return panel

    def load(self, objects_to_draw, absolute_frames, current_frames):
        continue_to_next_frame = False

        for panel in self._panels:
            should_render, at_last_frame = panel._display(current_frames)

            if should_render:
                for obj in panel._objects:
                    objects_to_draw.append(obj)

            if not at_last_frame:
                continue_to_next_frame = True

        return continue_to_next_frame

