import pygame as pg
import random
import time

class Tetris:
    def __init__(self, window_size):
        # Window game setup
        self.window = pg.display.set_mode((window_size * 14, window_size * 20))

        # Fonte setup
        pg.font.init()
        self.font = pg.font.SysFont("Courier New", window_size, bold=True)

        self.clock = pg.time.Clock()
        self.time = 0

        # Colors
        self.black       = (  0,   0,   0)
        self.white       = (255, 255, 255)
        self.gray        = (150, 150, 150) # color code 'x'
        self.purple      = (171,  57, 219) # color code 'p'
        self.blue        = ( 23,  31, 223) # color code 'b'
        self.light_blue  = (  3, 133, 166) # color code 'l'
        self.red         = (246,  51,  73) # color code 'r'
        self.orange      = (250, 123,  21) # color code 'o'
        self.yellow      = (245, 198,  42) # color code 'y'
        self.green       = ( 99, 209,  21) # color code 'g'

        # Mouse variables
        self.last_click_status = (False, False, False)

        # Game variables
        self.starting_first_game = True
        self.show_restart_button = True
        self.board_square = window_size
        self.next_shapes_list = ['', '', '', '']
        self.score = 0
        self.speed = 1
        self.selected_form = 'shape_1'
        self.shape_pos = [4, 0]
        self.shape_matrix = [[]]
        self.new_shape = True

        # Formato doss blocos
        self.shape = {
            'shape_1': {
                'shape': [[1, 1],
                          [1, 1]],
                'color': self.yellow
            },
            'shape_2': {
                'shape': [[0, 1, 0],
                          [1, 1, 1]],
                'color': self.purple
            },
            'shape_3': {
                'shape': [[1, 1, 1, 1]],
                'color': self.light_blue
            },
            'shape_4': {
                'shape': [[1, 1, 0],
                          [0, 1, 1]],
                'color': self.red
            },
            'shape_5': {
                'shape': [[0, 1, 1],
                          [1, 1, 0]],
                'color': self.green
            },
            'shape_6': {
                'shape': [[1, 0, 0],
                          [1, 1, 1]],
                'color': self.blue
            },
            'shape_7': {
                'shape': [[0, 0, 1],
                          [1, 1, 1]],
                'color': self.orange
            }
        }

        self.map = [['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', '']]

                    
