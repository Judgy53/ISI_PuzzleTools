
import random
from typing import Any

from pygame import Surface
import pygame
from pygame.event import Event
from shiftingBlock.SaveManager import ImportData, SaveManager
from shiftingBlock.Block import Block
from shiftingBlock.BlockShape import BlockShape
from shiftingBlock.Grid import Grid
from shiftingBlock.Scene.Scene import Scene
from shiftingBlock.Scene.SceneSetGoal import SceneSetGoal


class SceneFillGrid(Scene):

    def initialize(self, data: dict[str, Any]) -> None:
        if not 'import' in data or not isinstance(data['import'], ImportData) or not data['import'].start_grid:
            raise ValueError("SceneFillGrid init data is missing import data")
        
        self.__import_data__: ImportData = data['import']
        self.__grid__: Grid = data['import'].start_grid
        self.__current_block_idx__: int = 0
        self.__last_cell_clicked__: tuple[int, int] = (-1, -1)

    def update(self) -> None:
        pass

    def process_key_event(self, event: Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        
        match event.key:
            case pygame.K_LEFT:
                self.__current_block_idx__ -= 1
            case pygame.K_RIGHT:
                self.__current_block_idx__ += 1
            case pygame.K_DELETE:
                if self.__current_block_idx__ < len(self.__grid__.blocks):
                    self.__grid__.blocks.pop(self.__current_block_idx__)
                    self.__grid__.__dirty_cache__ = True
            case pygame.K_c:
                if self.__current_block_idx__ < len(self.__grid__.blocks):
                    self.__grid__.blocks[self.__current_block_idx__].color = pygame.Color(random.randint(0, 255), random.randint(0, 255),random.randint(0, 255))
            case pygame.K_e:
                SaveManager.try_export(self.__grid__)
            case pygame.K_i:
                if import_data := SaveManager.try_import():
                    self.__import_data__ = import_data
                    if grid := import_data.start_grid:
                        self.__grid__ = grid
            case pygame.K_RETURN:
                self.__import_data__.start_grid = self.__grid__
                Scene._change_scene(SceneSetGoal, {'import': self.__import_data__})

        self.__current_block_idx__ = max(0, self.__current_block_idx__)
        self.__current_block_idx__ = min(len(self.__grid__.blocks), self.__current_block_idx__)

    def process_mouse_event(self, event: Event, screen_rect: pygame.Rect) -> None:
        #if event.type != pygame.MOUSEBUTTONDOWN or not pygame.mouse.get_pressed()[0]:
        if event.type == pygame.MOUSEBUTTONUP:
            self.__last_cell_clicked__ = (-1, -1)

        if not pygame.mouse.get_pressed()[0]:
            return
        
        (c_x, c_y) = self._get_cell_at_screen_pos(screen_rect, pygame.mouse.get_pos())
        if c_x < 0 or c_y < 0 or self.__last_cell_clicked__ == (c_x, c_y):
            return
        
        self.__last_cell_clicked__ = (c_x, c_y)
        
        block_at_pos: Block | None = self.__grid__.get_block_at_pos(c_x, c_y)
        current_block: Block | None = self._get_current_block()
        if block_at_pos == None:
            if current_block == None:
                color: pygame.Color = pygame.Color(random.randint(0, 255), random.randint(0, 255),random.randint(0, 255))
                self.__grid__.add_block_if_legal(Block(self.__current_block_idx__, c_x, c_y, BlockShape([[True]]),  color))
            elif self.__grid__.blocks[self.__current_block_idx__].try_add_cell(c_x, c_y):
                self.__grid__.__dirty_cache__ = True
        elif current_block != None and self.__grid__.blocks[self.__current_block_idx__] == block_at_pos:
            if block_at_pos.try_remove_cell(c_x, c_y):
                self.__grid__.__dirty_cache__ = True


    def draw(self, screen: Surface) -> None:
        block_id: str = f'Block {self.__current_block_idx__}'
        super()._draw_text_default_font(screen, block_id, (10, 10))

        grid_rect: pygame.Rect = self._get_grid_rect(screen.get_rect())
        self.__grid__.draw(screen, grid_rect, self.__current_block_idx__)

    def _get_grid_rect(self, screen_rect:pygame.Rect) -> pygame.Rect:
        return super()._offset_rect(screen_rect, pygame.Rect(0, 50, 0, -70))
    
    def _get_cell_at_screen_pos(self, screen_rect: pygame.Rect, click_pos: tuple[int, int]) -> tuple[int, int]:
        grid_rect: pygame.Rect = self._get_grid_rect(screen_rect)
        if not grid_rect.collidepoint(click_pos):
            return (-1, -1)
        
        cell_size: int = self.__grid__.get_cell_screen_size(grid_rect)
        grid_click_pos: tuple[int, int] = super()._offset_pos(click_pos, (grid_rect.left * -1, grid_rect.top * -1))
        clicked_cell: tuple[int, int] = (grid_click_pos[0] // cell_size, grid_click_pos[1] // cell_size)

        if clicked_cell[0] >= self.__grid__.width or clicked_cell[1] >= self.__grid__.height:
            return (-1, -1)
        
        return clicked_cell
    
    def _get_current_block(self) -> Block | None:
        if self.__current_block_idx__ >= len(self.__grid__.blocks):
            return None
        return self.__grid__.blocks[self.__current_block_idx__]
