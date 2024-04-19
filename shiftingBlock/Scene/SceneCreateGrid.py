from typing import Any
from pygame import Surface
import pygame
from pygame.event import Event
from shiftingBlock.SaveManager import ImportData, SaveManager
from shiftingBlock.Grid import Grid
from shiftingBlock.Scene.Scene import Scene

class SceneCreateGrid(Scene):

    def initialize(self, _: dict[str, Any]) -> None:
        self.__grid__: Grid = Grid(10, 5)
    
    def update(self) -> None:
        return super().update()
    
    def process_key_event(self, event: Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        
        match event.key:
            case pygame.K_LEFT:
                self.__resizeGrid__(-1, 0)
            case pygame.K_RIGHT:
                self.__resizeGrid__(1, 0)
            case pygame.K_UP:
                self.__resizeGrid__(0, 1)
            case pygame.K_DOWN:
                self.__resizeGrid__(0, -1)
            case pygame.K_i:
                if import_data := SaveManager.try_import():
                    from shiftingBlock.Scene.SceneFillGrid import SceneFillGrid
                    Scene._change_scene(SceneFillGrid, {'import': import_data})
            case pygame.K_RETURN:
                from shiftingBlock.Scene.SceneFillGrid import SceneFillGrid
                Scene._change_scene(SceneFillGrid, {'import': ImportData(self.__grid__, None, None)})

    def draw(self, screen: Surface) -> None:
        size_str: str = "←→{} x {}↓↑".format(self.__grid__.width, self.__grid__.height)
        super()._draw_text_default_font(screen, size_str, (10, 10))

        grid_rect: pygame.Rect = self._get_grid_rect(screen.get_rect())
        self.__grid__.draw(screen, grid_rect)

    def __resizeGrid__(self, shift_x: int, shift_y: int) -> None:
        self.__grid__.width = max(1, self.__grid__.width + shift_x)
        self.__grid__.height = max(1, self.__grid__.height + shift_y)

    def _get_grid_rect(self, screen_rect:pygame.Rect) -> pygame.Rect:
        return super()._offset_rect(screen_rect, pygame.Rect(0, 50, 0, -70))