#Versão restruturada do do jogo

import pygame as pg
import random
import time
import sys
import math
from typing import List, Tuple, Dict, Optional, Any
from enum import Enum, auto
from dataclasses import dataclass, field
from collections import deque
import json
import os


class GameConfiguration:
    
    @staticmethod
    class WindowSettings:
        BASE_TILE_SIZE = 42
        GRID_WIDTH = 10
        GRID_HEIGHT = 20
        SCREEN_MULTIPLIER_X = 18
        SCREEN_MULTIPLIER_Y = 20
        WINDOW_WIDTH = BASE_TILE_SIZE * SCREEN_MULTIPLIER_X
        WINDOW_HEIGHT = BASE_TILE_SIZE * SCREEN_MULTIPLIER_Y
        FPS_LIMIT = 60
        WINDOW_TITLE = "POP BLOCK"
        
    @staticmethod
    class ColorSystem:
         
         #cores
        
        @staticmethod
        def get_color_palette() -> Dict[str, Tuple[int, int, int]]:
            
            return {
                'PRETO': (0, 0, 0),
                'WHITE': (255, 255, 255),
                'GRAY': (150, 150, 150),
                'PURPLE': (171, 57, 219),
                'BLUE': (23, 31, 223),
                'LIGHT_BLUE': (3, 133, 166),
                'RED': (246, 51, 73),
                'ORANGE': (250, 123, 21),
                'YELLOW': (245, 198, 42),
                'GREEN': (99, 209, 21),
                'DARK_GRAY': (50, 50, 50),
                'HIGHLIGHT_GRAY': (180, 180, 180),
                'BUTTON_GREEN': (0, 200, 0),
                'BUTTON_HOVER': (0, 250, 0),
                'BACKGROUND': (15, 15, 35),
                'GRID_LINE': (80, 80, 80)
            }
        
        @staticmethod
        def get_color_code_mapping() -> Dict[str, str]:
            """Códigps de cor"""
            return {
                'p': 'PURPLE',
                'b': 'BLUE',
                'l': 'LIGHT_BLUE',
                'r': 'RED',
                'o': 'ORANGE',
                'y': 'YELLOW',
                'g': 'GREEN',
                'x': 'GRAY'
            }
    
    @staticmethod
    class GameParameters:
        
        INITIAL_SPEED = 1
        MAX_SPEED = 50
        SCORE_INCREMENT_BASE = 100
        LINE_CLEAR_SCORE = 10
        SPEED_INCREASE_THRESHOLD = 100
        FALL_TIME_BASE = 60
        PREVIEW_SHAPES_COUNT = 4
        GRID_WIDTH = 10
        GRID_HEIGHT = 20


class GameEventType(Enum):
    
    SHAPE_LOCKED = auto()
    LINE_CLEARED = auto()
    GAME_OVER = auto()
    GAME_STARTED = auto()
    GAME_RESTARTED = auto()
    SCORE_UPDATED = auto()
    LEVEL_CHANGED = auto()
    SHAPE_ROTATED = auto()
    SHAPE_MOVED = auto()

@dataclass
class GameEvent:
    event_type: GameEventType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

class EventDispatcher:
    
    
    def __init__(self):
        self._listeners: Dict[GameEventType, List] = {}
        
    def add_listener(self, event_type: GameEventType, callback):

        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
        
    def dispatch_event(self, event: GameEvent):
        
        if event.event_type in self._listeners:
            for callback in self._listeners[event.event_type]:
                callback(event)

#  Formas
class TetrominoType(Enum):
    """forma dos blpcoss"""
    O = auto()  # Quadrado
    I = auto()  # Linha
    T = auto()  # 'T'
    L = auto()  # L normal
    J = auto()  # L invertido
    S = auto()  # S
    Z = auto()  # Z

@dataclass
class TetrominoDefinition:
    
    shape_type: TetrominoType
    shape_matrix: List[List[int]]
    color_name: str
    rotation_states: List[List[List[int]]] = field(default_factory=list)
    
    def __post_init__(self):
        
        self.rotation_states = self._generate_all_rotations()
    
    def _generate_all_rotations(self) -> List[List[List[int]]]:
        rotations = [self.shape_matrix]
        current = self.shape_matrix
        
        for _ in range(3):
            # Rotação 90 graus pra direita
            rotated = list(zip(*current[::-1]))
            rotations.append([list(row) for row in rotated])
            current = rotated
            
        return rotations

class TetrominoFactory:
    
    
    def __init__(self):
        self.color_system = GameConfiguration.ColorSystem()
        self.definitions = self._create_definitions()
        
    def _create_definitions(self) -> Dict[TetrominoType, TetrominoDefinition]:
        
        colors = self.color_system.get_color_palette()
        
        return {
            TetrominoType.O: TetrominoDefinition(
                shape_type=TetrominoType.O,
                shape_matrix=[[1, 1], [1, 1]],
                color_name='YELLOW'
            ),
            TetrominoType.I: TetrominoDefinition(
                shape_type=TetrominoType.I,
                shape_matrix=[[1, 1, 1, 1]],
                color_name='LIGHT_BLUE'
            ),
            TetrominoType.T: TetrominoDefinition(
                shape_type=TetrominoType.T,
                shape_matrix=[[0, 1, 0], [1, 1, 1]],
                color_name='PURPLE'
            ),
            TetrominoType.L: TetrominoDefinition(
                shape_type=TetrominoType.L,
                shape_matrix=[[1, 0, 0], [1, 1, 1]],
                color_name='ORANGE'
            ),
            TetrominoType.J: TetrominoDefinition(
                shape_type=TetrominoType.J,
                shape_matrix=[[0, 0, 1], [1, 1, 1]],
                color_name='BLUE'
            ),
            TetrominoType.S: TetrominoDefinition(
                shape_type=TetrominoType.S,
                shape_matrix=[[0, 1, 1], [1, 1, 0]],
                color_name='GREEN'
            ),
            TetrominoType.Z: TetrominoDefinition(
                shape_type=TetrominoType.Z,
                shape_matrix=[[1, 1, 0], [0, 1, 1]],
                color_name='RED'
            )
        }
    
    def create_random(self) -> TetrominoType:
        """Cria forma aleatória"""
        return random.choice(list(self.definitions.keys()))
    
    def get_definition(self, shape_type: TetrominoType) -> TetrominoDefinition:
        
        return self.definitions[shape_type]
    
    def get_color_by_code(self, color_code: str) -> Tuple[int, int, int]:
        
        color_name = self.color_system.get_color_code_mapping().get(color_code, 'GRAY')
        return self.color_system.get_color_palette()[color_name]

#  GRADE do Jogo
class GameGrid:
    
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.cells: List[List[str]] = self._create_empty_grid()
        
    def _create_empty_grid(self) -> List[List[str]]:
        #grade vazia
        return [['' for _ in range(self.width)] for _ in range(self.height)]
    
    def clear(self):
        """Limpa toda a grade"""
        self.cells = self._create_empty_grid()
    
    def place_tetromino(self, tetromino: 'ActiveTetromino') -> bool:
        """Coloca um tetrominó na grade"""
        shape_def = tetromino.get_current_shape()
        color_code = tetromino.color_code
        
        for y, row in enumerate(shape_def.shape_matrix):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = tetromino.position[0] + x
                    grid_y = tetromino.position[1] + y
                    
                    if (0 <= grid_x < self.width and 
                        0 <= grid_y < self.height and 
                        self.cells[grid_y][grid_x] == ''):
                        self.cells[grid_y][grid_x] = color_code
                    else:
                        return False
        return True
    
    def check_line_completions(self) -> List[int]:
        """Verifica linhas completas"""
        completed_rows = []
        
        for y in range(self.height):
            if all(cell != '' for cell in self.cells[y]):
                completed_rows.append(y)
                
        return completed_rows
    
    def remove_lines(self, rows: List[int]):
        """tira linhas inteiras"""
        rows.sort()
        
        for row in rows:
            # tira a linha 
            del self.cells[row]
            # Adiciona nova linha 
            self.cells.insert(0, ['' for _ in range(self.width)])
    
    def is_collision(self, tetromino: 'ActiveTetromino', 
                    offset_x: int = 0, offset_y: int = 0) -> bool:
        """Verifica colisão com ma grade"""
        shape_def = tetromino.get_current_shape()
        
        for y, row in enumerate(shape_def.shape_matrix):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = tetromino.position[0] + x + offset_x
                    grid_y = tetromino.position[1] + y + offset_y
                    
                    
                    if grid_x < 0 or grid_x >= self.width or grid_y >= self.height:
                        return True
                    
                    if grid_y >= 0 and self.cells[grid_y][grid_x] != '':
                        return True
                        
        return False


class ActiveTetromino:
    """Representa um tetrominó ativo no jogo"""
    
    def __init__(self, shape_type: TetrominoType, factory: TetrominoFactory):
        self.shape_type = shape_type
        self.factory = factory
        self.definition = factory.get_definition(shape_type)
        self.rotation_index = 0
        self.position = [4, 0]  
        self.color_code = self._get_color_code()
        
    def _get_color_code(self) -> str:
        """Obtém o código de cor do tetrominó"""
        color_mapping = {
            TetrominoType.O: 'y',
            TetrominoType.I: 'l',
            TetrominoType.T: 'p',
            TetrominoType.L: 'o',
            TetrominoType.J: 'b',
            TetrominoType.S: 'g',
            TetrominoType.Z: 'r'
        }
        return color_mapping[self.shape_type]
    
    def get_current_shape(self) -> TetrominoDefinition:
        
        rotated_matrix = self.definition.rotation_states[self.rotation_index]
        return TetrominoDefinition(
            shape_type=self.shape_type,
            shape_matrix=rotated_matrix,
            color_name=self.definition.color_name
        )
    
    def rotate(self, direction: int, grid: GameGrid) -> bool:
        
        old_rotation = self.rotation_index
        
        if direction > 0:  # Rotação no sentido horarrio
            self.rotation_index = (self.rotation_index + 1) % 4
        else:  
            self.rotation_index = (self.rotation_index - 1) % 4
        
        if grid.is_collision(self):
            self.rotation_index = old_rotation
            return False
            
        return True
    
    def move(self, dx: int, dy: int, grid: GameGrid) -> bool:
        if not grid.is_collision(self, dx, dy):
            self.position[0] += dx
            self.position[1] += dy
            return True
        return False
    
    def hard_drop(self, grid: GameGrid):
        #bloco cai instataneamente
        while self.move(0, 1, grid):
            pass

#pontos
class ScoreManager:
    
    def __init__(self):
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.combo = 0
        self.multiplier = 1.0
        
    def add_shape_score(self, tetromino: ActiveTetromino):
        shape_def = tetromino.get_current_shape()
        block_count = sum(sum(row) for row in shape_def.shape_matrix)
        self.score += int(block_count * 10 * self.multiplier)
        
    def add_line_clear_score(self, lines_count: int):
        line_scores = {1: 100, 2: 300, 3: 500, 4: 800}
        base_score = line_scores.get(lines_count, 0)
        
        # Bônus de combo
        combo_bonus = self.combo * 50
        
        self.score += int((base_score + combo_bonus) * self.multiplier)
        self.lines_cleared += lines_count
        
        # Atualizar combo
        if lines_count > 0:
            self.combo += 1
        else:
            self.combo = 0
            
        # Atualizar nível
        self.level = self.lines_cleared // 10 + 1
        
        # Atualizar multiplicador baseado no nível
        self.multiplier = 1.0 + (self.level - 1) * 0.1
        
    def reset(self):
        '''zerar pontuação'''
        self.__init__()

#controles
class InputHandler:
    
    def __init__(self):
        self.key_map = {
            pg.K_LEFT: 'left',
            pg.K_a: 'left',
            pg.K_RIGHT: 'right', 
            pg.K_d: 'right',
            pg.K_DOWN: 'down',
            pg.K_s: 'down',
            pg.K_UP: 'rotate_cw',
            pg.K_e: 'rotate_cw',
            pg.K_q: 'rotate_ccw',
            pg.K_SPACE: 'hard_drop',
            pg.K_ESCAPE: 'quit',
            pg.K_p: 'pause',
            pg.K_r: 'restart'
        }
        
        self.key_states = {}
        self.key_pressed = {}
        
    def update(self):
    
        current_keys = pg.key.get_pressed()
        
        for key_code, action in self.key_map.items():
            current_state = current_keys[key_code] if key_code < len(current_keys) else False
            previous_state = self.key_states.get(key_code, False)
            
            self.key_pressed[action] = current_state and not previous_state
            self.key_states[key_code] = current_state
    
    def is_pressed(self, action: str) -> bool:
        
        return self.key_pressed.get(action, False)
    
    def is_held(self, action: str) -> bool:
        
        key_code = next((k for k, v in self.key_map.items() if v == action), None)
        if key_code:
            return self.key_states.get(key_code, False)
        return False

class MouseHandler:
    
    def __init__(self):
        self.position = (0, 0)
        self.buttons = (False, False, False)
        self.click_events = (False, False, False)
        self.previous_buttons = (False, False, False)
        
    def update(self):
        self.position = pg.mouse.get_pos()
        self.buttons = pg.mouse.get_pressed()
        
        self.click_events = (
            self.buttons[0] and not self.previous_buttons[0],
            self.buttons[1] and not self.previous_buttons[1],
            self.buttons[2] and not self.previous_buttons[2]
        )
        
        self.previous_buttons = self.buttons
    
    def get_click_position(self):
        if any(self.click_events):
            return self.position
        return None

#render
class RenderSystem:
    
    def __init__(self, window_size: Tuple[int, int], tile_size: int):
        self.window_size = window_size
        self.tile_size = tile_size
        self.colors = GameConfiguration.ColorSystem.get_color_palette()
        self.font_cache = {}
        
    def get_font(self, size: int, bold: bool =False):
        
        key = (size, bold)
        if key not in self.font_cache:
            self.font_cache[key] = pg.font.SysFont("Russo One", size, bold=False)
        return self.font_cache[key]
    
    def draw_grid(self, surface: pg.Surface, grid: GameGrid, factory: TetrominoFactory):
        
        # Desenha célula preenchidas
        for y in range(grid.height):
            for x in range(grid.width):
                if grid.cells[y][x]:
                    color_code = grid.cells[y][x]
                    color = factory.get_color_by_code(color_code)
                    
                    self.draw_block(
                        surface,
                        x * self.tile_size,
                        y * self.tile_size,
                        color
                    )
        
        for x in range(grid.width + 1):
            pg.draw.line(
                surface,
                self.colors['GRID_LINE'],
                (x * self.tile_size, 0),
                (x * self.tile_size, grid.height * self.tile_size),
                1
            )
            
        for y in range(grid.height + 1):
            pg.draw.line(
                surface,
                self.colors['GRID_LINE'],
                (0, y * self.tile_size),
                (grid.width * self.tile_size, y * self.tile_size),
                1
            )
    
    def draw_block(self, surface: pg.Surface, x: int, y: int, color: Tuple[int, int, int]):
        """Desenha um bloco individual"""
        # Bloco principal
        pg.draw.rect(
            surface,
            color,
            (x, y, self.tile_size, self.tile_size)
        )
        
        # Borda interna ç
        highlight_color = tuple(min(c + 40, 255) for c in color)
        pg.draw.rect(
            surface,
            highlight_color,
            (x + 2, y + 2, self.tile_size - 4, self.tile_size - 4),
            2
        )
        
        # Sombra
        shadow_color = tuple(max(c - 40, 0) for c in color)
        pg.draw.rect(
            surface,
            shadow_color,
            (x + self.tile_size - 3, y + 2, 2, self.tile_size - 4)
        )
        pg.draw.rect(
            surface,
            shadow_color,
            (x + 2, y + self.tile_size - 3, self.tile_size - 4, 2)
        )
    
    def draw_tetromino(self, surface: pg.Surface, tetromino: ActiveTetromino):
        #tertis ativo
        shape_def = tetromino.get_current_shape()
        color = tetromino.factory.get_color_by_code(tetromino.color_code)
        
        for y, row in enumerate(shape_def.shape_matrix):
            for x, cell in enumerate(row):
                if cell:
                    block_x = (tetromino.position[0] + x) * self.tile_size
                    block_y = (tetromino.position[1] + y) * self.tile_size
                    self.draw_block(surface, block_x, block_y, color)
    
    def draw_preview(self, surface: pg.Surface, preview_shapes: List[TetrominoType], 
                    factory: TetrominoFactory):
        """Draw das proximas peças"""
        start_x = 10 * self.tile_size + 60
        start_y = 50
        
        # Título
        title_font = self.get_font(self.tile_size // 2, True)
        title_text = title_font.render("PRÓXIMO BLOCO", True, self.colors['WHITE'])
        surface.blit(title_text, (start_x, start_y - 40))
        
        for i, shape_type in enumerate(preview_shapes[:4]):
            shape_def = factory.get_definition(shape_type)
            color = factory.get_color_by_code(
                {'YELLOW': 'y', 'LIGHT_BLUE': 'l', 'PURPLE': 'p', 
                 'ORANGE': 'o', 'BLUE': 'b', 'GREEN': 'g', 'RED': 'r'}[shape_def.color_name]
            )
            
            preview_y = start_y + i * (self.tile_size * 3 + 10)
            pg.draw.rect(
                surface,
                self.colors['DARK_GRAY'],
                (start_x - 10, preview_y - 10, self.tile_size * 4 + 20, self.tile_size * 3 + 20),
                border_radius=5
            )
            
            # DRAW NA PEÇA DO CENTRO
            shape_width = len(shape_def.shape_matrix[0]) * self.tile_size
            shape_height = len(shape_def.shape_matrix) * self.tile_size
            
            offset_x = start_x + (self.tile_size * 4 - shape_width) // 2
            offset_y = preview_y + (self.tile_size * 3 - shape_height) // 2
            
            for y, row in enumerate(shape_def.shape_matrix):
                for x, cell in enumerate(row):
                    if cell:
                        block_x = offset_x + x * self.tile_size
                        block_y = offset_y + y * self.tile_size
                        self.draw_block(surface, block_x, block_y, color)
    
    def draw_score_panel(self, surface: pg.Surface, score_manager: ScoreManager):
        """DRAW PONTOS"""
        panel_x = 10 * self.tile_size + 20
        panel_y = 300
        
        font = self.get_font(self.tile_size // 2)
        
        # Fundo do painel
        pg.draw.rect(
            surface,
            self.colors['DARK_GRAY'],
            (panel_x - 10, panel_y - 10, 200, 200),
            border_radius=5
        )
        
        info_lines = [
            f"PONTOS: {score_manager.score}",
            f"NÍVEL: {score_manager.level}",
            f"LINHAS: {score_manager.lines_cleared}",
            f"COMBO: x{score_manager.combo}",
            f"MULT. : x{score_manager.multiplier:.1f}"
        ]
        
        for i, line in enumerate(info_lines):
            text = font.render(line, True, self.colors['WHITE'])
            surface.blit(text, (panel_x, panel_y + i * 25))
    
    def draw_game_over(self, surface: pg.Surface, score: int):
        overlay = pg.Surface(self.window_size, pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        large_font = self.get_font(self.tile_size * 2, True)
        medium_font = self.get_font(self.tile_size, True)
        
        # game Over.
        game_over_text = large_font.render("GAME OVER", True, self.colors['RED'])
        surface.blit(
            game_over_text,
            (self.window_size[0] // 2 - game_over_text.get_width() // 2,
             self.window_size[1] // 3)
        )
        
        # Pontos finais
        score_text = medium_font.render(f"Pontuação Final: {score}", True, self.colors['GREEN'])
        surface.blit(
            score_text,
            (self.window_size[0] // 2 - score_text.get_width() // 2,
             self.window_size[1] // 2)
        )
        
        # Instruções
        restart_text = medium_font.render("Pressione R para reiniciar", True, self.colors['YELLOW'])
        surface.blit(
            restart_text,
            (self.window_size[0] // 2 - restart_text.get_width() // 2,
             self.window_size[1] * 2 // 3)
        )
        
    def draw_pause_screen(self, surface: pg.Surface):
        overlay = pg.Surface(self.window_size, pg.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        
        font = self.get_font(self.tile_size * 2, True)
        pause_text = font.render("PAUSADO", True, self.colors['BLUE'])
        surface.blit(
            pause_text,
            (self.window_size[0] // 2 - pause_text.get_width() // 2,
             self.window_size[1] // 2 - pause_text.get_height() // 2)
        )


class TetrisGameEngine:
    def _setup_audio(self):
        try:
            pg.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            print("Mixer inicializado com sucesso")
            
            music_files = [
                'tetris_music.mp3',]
            
            music_loaded = False
            for music_file in music_files:
                try:
                    if os.path.exists(music_file):
                        pg.mixer.music.load(music_file)
                        print(f"Música carregada: {music_file}")
                        music_loaded = True
                        break
                except:
                    continue
            
            if music_loaded:
                pg.mixer.music.set_volume(0.3)
                pg.mixer.music.play(-1)  # -1 para loop infinito
                
            else:
                print("Nenhum arquivo de música encontrado")
        
        except Exception as e:
            print(f"Erro ao configurar áudio: {e}")
    
    def __init__(self):
    
    
        self._setup_audio()
    
        
        # Inicialização da janela
        pg.init()
        
        # Configs
        self.window_settings = GameConfiguration.WindowSettings()
        
        self.screen = pg.display.set_mode(
            (self.window_settings.WINDOW_WIDTH, self.window_settings.WINDOW_HEIGHT)
        )
        pg.display.set_caption(self.window_settings.WINDOW_TITLE)
        
        self.clock = pg.time.Clock()
        self.event_dispatcher = EventDispatcher()
        self.input_handler = InputHandler()
        self.mouse_handler = MouseHandler()
        self.score_manager = ScoreManager()
        
        self.tetromino_factory = TetrominoFactory()
        
# Grade do jogo
        self.grid = GameGrid(
            GameConfiguration.GameParameters.GRID_WIDTH,
            GameConfiguration.GameParameters.GRID_HEIGHT
        )
        
        self.renderer = RenderSystem(
            (self.window_settings.WINDOW_WIDTH, self.window_settings.WINDOW_HEIGHT),
            self.window_settings.BASE_TILE_SIZE
        )

        self.current_tetromino = None
        self.preview_shapes = []
        self.game_over = False
        self.paused = False
        self.fall_timer = 0
        self.fall_speed = GameConfiguration.GameParameters.FALL_TIME_BASE
        
        # Inicialização
        self._initialize_game()
        
        self._setup_event_handlers()
    
    def _initialize_game(self):
        """Inicializa o estado do jogo"""
        
        self.preview_shapes = [
            self.tetromino_factory.create_random() for _ in range(10)
        ]
        
        
        self._get_next_tetromino()
        
    
        self.game_over = False
        self.paused = False
        self.fall_timer = 0
        self.score_manager.reset()
        self.grid.clear()
        
        
        self.event_dispatcher.dispatch_event(
            GameEvent(GameEventType.GAME_STARTED)
        )
    
    def _setup_event_handlers(self):
        
        self.event_dispatcher.add_listener(
            GameEventType.LINE_CLEARED,
            self._on_line_cleared
        )
        
        self.event_dispatcher.add_listener(
            GameEventType.GAME_OVER,
            self._on_game_over
        )
    
    def _on_line_cleared(self, event: GameEvent):
        
        lines_count = event.data.get('lines', 0)
        self.score_manager.add_line_clear_score(lines_count)
        

        self.fall_speed = max(
            10,
            GameConfiguration.GameParameters.FALL_TIME_BASE - 
            (self.score_manager.level - 1) * 5
        )
    
    def _on_game_over(self, event: GameEvent):
        """Handler para game over"""
        self.game_over = True
    
    def _get_next_tetromino(self):
        if self.preview_shapes:
            next_shape = self.preview_shapes.pop(0)
            self.current_tetromino = ActiveTetromino(next_shape, self.tetromino_factory)
            
            
            self.preview_shapes.append(self.tetromino_factory.create_random())
            
            
            if self.grid.is_collision(self.current_tetromino):
                self.event_dispatcher.dispatch_event(
                    GameEvent(GameEventType.GAME_OVER)
                )
        else:
            self.event_dispatcher.dispatch_event(
                GameEvent(GameEventType.GAME_OVER)
            )
    
    def _handle_input(self):

        self.input_handler.update()
        
        if self.input_handler.is_pressed('quit'):
            pg.quit()
            sys.exit()
            
        if self.input_handler.is_pressed('restart'):
            self._initialize_game()
            return
            
        if self.input_handler.is_pressed('pause'):
            self.paused = not self.paused
            
        if self.game_over or self.paused or not self.current_tetromino:
            return
            
        # Movimento da peça
        if self.input_handler.is_pressed('left'):
            self.current_tetromino.move(-1, 0, self.grid)
        elif self.input_handler.is_pressed('right'):
            self.current_tetromino.move(1, 0, self.grid)
        elif self.input_handler.is_pressed('down'):
            self.current_tetromino.move(0, 1, self.grid)
            
        # Rotação
        if self.input_handler.is_pressed('rotate_cw'):
            self.current_tetromino.rotate(1, self.grid)
        elif self.input_handler.is_pressed('rotate_ccw'):
            self.current_tetromino.rotate(-1, self.grid)
            
        #CAIR RÁPIDO
        if self.input_handler.is_pressed('hard_drop'):
            self.current_tetromino.hard_drop(self.grid)
            self._lock_current_tetromino()
    
    def _lock_current_tetromino(self):
        #FIXA BLOCO
        if self.current_tetromino:
           
            self.score_manager.add_shape_score(self.current_tetromino)
            
            
            success = self.grid.place_tetromino(self.current_tetromino)
            
            if not success:
                self.event_dispatcher.dispatch_event(
                    GameEvent(GameEventType.GAME_OVER)
                )
                return
            
            
            completed_rows = self.grid.check_line_completions()
            if completed_rows:
                self.grid.remove_lines(completed_rows)
                self.event_dispatcher.dispatch_event(
                    GameEvent(
                        GameEventType.LINE_CLEARED,
                        {'lines': len(completed_rows)}
                    )
                )
            
            
            self._get_next_tetromino()
    
    def _update_game_logic(self):
        """Atualiza a lógica do jogo"""
        if self.game_over or self.paused or not self.current_tetromino:
            return
            
        self.fall_timer += 1
        if self.fall_timer >= self.fall_speed:
            if not self.current_tetromino.move(0, 1, self.grid):
                self._lock_current_tetromino()
            self.fall_timer = 0
    
    def _render(self):
        """Renderiza o jogo"""
        # Fundo
        self.screen.fill(GameConfiguration.ColorSystem.get_color_palette()['BACKGROUND'])
        
        self.renderer.draw_grid(self.screen, self.grid, self.tetromino_factory)
        
        if self.current_tetromino:
            self.renderer.draw_tetromino(self.screen, self.current_tetromino)
        
        self.renderer.draw_preview(self.screen, self.preview_shapes, self.tetromino_factory)
        
        # Painel Ponts
        self.renderer.draw_score_panel(self.screen, self.score_manager)
        
        if self.game_over:
            self.renderer.draw_game_over(self.screen, self.score_manager.score)
        
        if self.paused:
            self.renderer.draw_pause_screen(self.screen)
        
        pg.display.flip()
    
    def run(self):
        print("=" * 60)
        print("POP BLOCK - Inicializando...")
        print(f"Resolução: {self.window_settings.WINDOW_WIDTH}x{self.window_settings.WINDOW_HEIGHT}")
        print(f"Tile Size: {self.window_settings.BASE_TILE_SIZE}")
        print("Controles: Setas/AWSD para mover, Q/E para rotacionar")
        print("Espaço: Hard Drop, P: Pausar, R: Reiniciar, ESC: Sair")
        print("=" * 60)
        
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            
            self.mouse_handler.update()
            
            self._handle_input()

            self._update_game_logic()
            
            self._render()
            
            self.clock.tick(GameConfiguration.WindowSettings.FPS_LIMIT)

print('=' * 60)
def main():
    try:
        game = TetrisGameEngine()
        game.run()
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
        pg.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()