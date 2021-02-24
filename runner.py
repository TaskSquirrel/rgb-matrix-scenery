import random
import sys
import time
import signal
from scene import Text, Panel, Scene, CenterHorizontally
from matrix import MatrixBase, Color, MatrixRunner

class State:
    def before(self):
        pass

class Counter(State):
    def before(self):
        self.counter = 0

    def update(self):
        self.owner.text = str(self.counter)
        self.counter = self.counter + 1

class Sliding(State):
    def before(self):
        self.position = self.matrix.cols

    def update(self):
        last_length = self.owner.last_length

        if last_length and last_length > 0:
            if self.position == -last_length:
                self.position = self.matrix.cols
            else:
                self.position = self.position - 1

            self.owner.x = self.position

class RandomColor(State):
    def update(self):
        self.owner.color = Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def runner():
    matrix = MatrixBase(32, 64)

    scene = Scene(matrix)
    panel = scene.create_panel()
    panel.duration(1)
    panel.add(Text('Hello', Color(255, 255, 255), 10, 15).do(Counter()).times(3).every(0.1).do(Sliding()))

    p_b = scene.create_panel()
    p_b.duration(1)
    p_b.add(Text('Lmao', Color(0, 255, 100), 15, 30).every(0.1).do(Sliding()).every(1).do(RandomColor()))

    runner = MatrixRunner(matrix, scene)
    runner.thread().start()

if __name__ == '__main__':
    runner()

