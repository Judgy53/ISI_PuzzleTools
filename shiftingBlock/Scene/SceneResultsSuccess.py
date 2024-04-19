from typing import Any

from pygame import Surface
import pygame
from pygame.event import Event
from shiftingBlock.Grid import Grid
from shiftingBlock.SaveManager import ImportData, SaveManager
from shiftingBlock.Scene.Scene import Scene


class SceneResultsSuccess(Scene):

    def initialize(self, data: dict[str, Any]) -> None:
        if not 'import' in data or not isinstance(data['import'], ImportData):
            raise ValueError('import not in data')
        self.__import_data__: ImportData = data['import']
        
        if not 'grid_solved' in data:
            raise ValueError('grid_solved not in data')
        
        self.__grid_solved__: Grid = data['grid_solved']
        self.__step_list__: list[Grid] = self.solved_grid_to_list(self.__grid_solved__)
        self.__current_step__: int = 0
    
    def solved_grid_to_list(self, grid: Grid | None) -> list[Grid]:
        out: list[Grid] = []

        while grid:
            out.append(grid)
            grid = grid.previous_grid

        out.reverse()
        return out

    def update(self) -> None:
        return super().update()

    def process_key_event(self, event: Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        
        match event.key:
            case pygame.K_LEFT:
                self.__current_step__ = max(0, self.__current_step__ - 1)
            case pygame.K_RIGHT:
                self.__current_step__ = min(len(self.__step_list__) - 1, self.__current_step__ + 1)
            case pygame.K_e:
                if start_grid := self.__import_data__.start_grid:
                    SaveManager.try_export(start_grid, self.__import_data__.goal_grid, self.__step_list__)
            case pygame.K_RETURN:
                self.__import_data__.solve_steps = [step for step in self.__step_list__]
                from shiftingBlock.Scene.SceneFillGrid import SceneFillGrid
                Scene._change_scene(SceneFillGrid, {'import': self.__import_data__})
            # case pygame.K_t:
            #     grid: Grid = self.__step_list__[self.__current_step__]
            #     for id in grid.blocks:
            #         print('{}: {}'.format(id, self.__step_list__[self.__current_step__].does_block_intersects_any(grid.blocks[id], id)))
    
    def draw(self, screen: Surface) -> None:
        Scene._draw_text_default_font(screen, f'Step {self.__current_step__ + 1} / {len(self.__step_list__)}', (10, 10))

        self.__step_list__[self.__current_step__].draw(screen, self._get_grid_rect(screen.get_rect()))

    def _get_grid_rect(self, screen_rect:pygame.Rect) -> pygame.Rect:
        return super()._offset_rect(screen_rect, pygame.Rect(0, 50, 0, -70))