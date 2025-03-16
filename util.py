import os
import sys
import pygame
import numpy as np

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def set_icon():
    pygame.display.set_icon(pygame.image.load(resource_path('./assets/logo.ico')))

def get_monitor():
    from const import Var
    pygame.display.init()
    Var.monitor_size = np.array(pygame.display.get_desktop_sizes()[0])
