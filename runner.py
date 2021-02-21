import sys
import time
import signal
from scene import Text, Panel, Scene
from matrix import MatrixBase, Color, MatrixThreader

def scenery():
    matrix = MatrixBase(32, 64)

    scene = Scene(matrix)
    panel = scene.create_panel()
    panel.duration(4)
    panel.add(Text('Hello', Color(255, 255, 255), 10, 15))

    p_b = scene.create_panel()
    p_b.delay(2)
    p_b.duration(3)
    p_b.add(Text('Fang', Color(0, 255, 100), 15, 30))

    thread = MatrixThreader(matrix, scene)
    thread.start()

if __name__ == '__main__':
    scenery()

