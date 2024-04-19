
from typing import Any

from pygame import Surface
from pygame.event import Event
import pygame
from shiftingBlock.Block import Block
from shiftingBlock.Grid import Grid
from shiftingBlock.SaveManager import ImportData, SaveManager
from shiftingBlock.Scene.Scene import Scene
from shiftingBlock.Scene.SceneSolve import SceneSolve

class SceneSetGoal(Scene):
    def initialize(self, data: dict[str, Any]) -> None:
        if not 'import' in data or not isinstance(data['import'], ImportData) or not data['import'].start_grid:
            raise ValueError('data does not contain a start_grid')
        
        self.__import_data__: ImportData = data['import']
        self.__start_grid__: Grid = data['import'].start_grid
        self.__goal_grid__: Grid = data['import'].goal_grid if data['import'].goal_grid else Grid(self.__start_grid__.width, self.__start_grid__.height)
        self.__current_block_idx__:int = 0

    def process_key_event(self, event: Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        
        match event.key:
            case pygame.K_LEFT:
                self.__current_block_idx__ = max(0, self.__current_block_idx__ - 1)
            case pygame.K_RIGHT:
                self.__current_block_idx__ = min(len(self.__start_grid__.blocks) - 1, self.__current_block_idx__ + 1)
            case pygame.K_DELETE:
                self._remove_current_goal_block()
            case pygame.K_e:
                SaveManager.try_export(self.__start_grid__, self.__goal_grid__)
            case pygame.K_i:
                if import_data := SaveManager.try_import():
                    from shiftingBlock.Scene.SceneFillGrid import SceneFillGrid
                    Scene._change_scene(SceneFillGrid, {'import': import_data})
            case pygame.K_ESCAPE:
                self.__import_data__.goal_grid = self.__goal_grid__
                from shiftingBlock.Scene.SceneFillGrid import SceneFillGrid
                Scene._change_scene(SceneFillGrid, {'import': self.__import_data__})
            case pygame.K_RETURN:
                self.__import_data__.goal_grid = self.__goal_grid__
                use_previous_solve: bool = pygame.key.get_mods() & pygame.KMOD_CTRL > 0
                Scene._change_scene(SceneSolve, {'import': self.__import_data__, 'use_previous_solve': use_previous_solve})
    
    def process_mouse_event(self, event: Event, screen_rect: pygame.Rect) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or not pygame.mouse.get_pressed()[0]:
            return
        
        if len(self.__start_grid__.blocks) == 0:
            return
        
        (c_x, c_y) = self._get_cell_at_screen_pos(screen_rect, pygame.mouse.get_pos())
        if c_x < 0 or c_y < 0:
            return
        
        block_at_pos: Block | None = self.__goal_grid__.get_block_at_pos(c_x, c_y)
        if self.__current_block_idx__ in self.__goal_grid__.blocks:
            if block_at_pos:
                self.__goal_grid__.blocks.pop(block_at_pos.id)
            return
        
        current_block: Block = self.__start_grid__.blocks[self.__current_block_idx__]
        goal_block: Block = current_block.copy()
        goal_block.x = c_x
        goal_block.y = c_y
        self.__goal_grid__.add_block_if_legal(goal_block)

    def _remove_current_goal_block(self) -> None:
        if len(self.__goal_grid__.blocks) >= self.__current_block_idx__:
            return
        
        self.__goal_grid__.blocks.pop(self.__current_block_idx__)

        self.__current_block_idx__ = min(len(self.__goal_grid__.blocks) - 1, self.__current_block_idx__)

    def update(self) -> None:
        pass

    def draw(self, screen: Surface) -> None:
        block_id: str = f'Block {self.__current_block_idx__}'
        super()._draw_text_default_font(screen, block_id, (10, 10))

        start_grid_rect: pygame.Rect = self._get_start_grid_rect(screen.get_rect())
        self.__start_grid__.draw(screen, start_grid_rect, self.__current_block_idx__)

        goal_grid_rect: pygame.Rect = self._get_goal_grid_rect(screen.get_rect())
        self.__goal_grid__.draw(screen, goal_grid_rect, self.__current_block_idx__)

    def _get_start_grid_rect(self, screen_rect:pygame.Rect) -> pygame.Rect:
        rect: pygame.Rect = super()._offset_rect(screen_rect, pygame.Rect(0, 50, 0, -70))

        # vertical layout
        rect_vert: pygame.Rect = rect.copy()
        rect_vert.height = (rect_vert.height // 2) - 10

        #horizontal_layout
        rect_horiz: pygame.Rect = rect.copy()
        rect_horiz.width = (rect_horiz.width // 2) - 10

        return max(rect_vert, rect_horiz, key=self.__start_grid__.get_cell_screen_size)
    
    def _get_goal_grid_rect(self, screen_rect:pygame.Rect) -> pygame.Rect:
        rect: pygame.Rect = super()._offset_rect(screen_rect, pygame.Rect(0, 50, 0, -70))

        # vertical layout
        rect_vert: pygame.Rect = rect.copy()
        rect_vert.height = (rect_vert.height // 2) - 10
        rect_vert.y = (screen_rect.height // 2) + 10

        #horizontal_layout
        rect_horiz: pygame.Rect = rect.copy()
        rect_horiz.width = (rect_horiz.width // 2) - 10
        rect_horiz.x = (screen_rect.width // 2) + 10

        return max(rect_vert, rect_horiz, key=self.__start_grid__.get_cell_screen_size)
    
    def _get_cell_at_screen_pos(self, screen_rect: pygame.Rect, click_pos: tuple[int, int]) -> tuple[int, int]:
        grid_rect: pygame.Rect = self._get_goal_grid_rect(screen_rect)
        if not grid_rect.collidepoint(click_pos):
            return (-1, -1)
        
        cell_size: int = self.__goal_grid__.get_cell_screen_size(grid_rect)
        (grid_x, grid_y) = super()._offset_pos(click_pos, (grid_rect.left * -1, grid_rect.top * -1))
        (cell_x, cell_y) = (grid_x // cell_size, grid_y // cell_size)

        if cell_x >= self.__goal_grid__.width or cell_y >= self.__goal_grid__.height:
            return (-1, -1)
        
        return (cell_x, cell_y)