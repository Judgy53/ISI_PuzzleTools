
from typing import Any
import pygame
from pygame.event import Event
from shiftingBlock.Block import Block
from shiftingBlock.BlockShape import BlockShape
from shiftingBlock.Grid import Grid
from shiftingBlock.Scene.Scene import Scene


class SceneTest(Scene):

    @staticmethod
    def get_scene_name() -> str:
        return 'Test'

    def initialize(self, data: dict[str, Any]) -> None:
        self.grid: Grid = data['grid'] if 'grid' in data else Grid(11, 5)

        self.grid.add_block_if_legal(Block(0, 0, 0, BlockShape([[True,True,True,True], [True,False,True,False], [True,False,False,False]]), pygame.Color(255, 0, 0)))
        self.grid.add_block_if_legal(Block(1, 1, 1, BlockShape([[True,False,False], [True,True,True]]), pygame.Color(0, 255, 0)))
        self.grid.add_block_if_legal(Block(2, 3, 3, BlockShape([[True,True,True,True]]), pygame.Color(0, 0, 255)))
        self.__drawGridBorders__: bool = True

        self.__selectedBlock__: int = 0
    
    def update(self) -> None:
        return super().update()
    
    def process_key_event(self, event: Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        
        match event.key:
            case pygame.K_RIGHT:
                self.__selectedBlock__ = (self.__selectedBlock__ + 1) % len(self.grid.blocks)
            case pygame.K_LEFT:
                self.__selectedBlock__ = self.__selectedBlock__ - 1 if self.__selectedBlock__ > -1 else len(self.grid.blocks) - 1
            case pygame.K_t:
                self.__drawGridBorders__ = not self.__drawGridBorders__

    def process_mouse_event(self, event: Event, screen_rect: pygame.Rect) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or not pygame.mouse.get_pressed()[0]:
            return
        
        clicked = self._get_cell_at_screen_pos(screen_rect, pygame.mouse.get_pos())
        if clicked[0] < 0 or clicked[1] < 0:
            return
        
        block_at_pos: Block | None = self.grid.get_block_at_pos(clicked[0], clicked[1])
        if block_at_pos == None:
            self.grid.blocks[self.__selectedBlock__].try_add_cell(clicked[0], clicked[1])
        elif self.grid.blocks[self.__selectedBlock__] == block_at_pos:
            block_at_pos.try_remove_cell(clicked[0], clicked[1])

    def draw(self, screen: pygame.Surface) -> None:
        gridDrawRect: pygame.Rect = pygame.Rect(0, 50, screen.get_width(), screen.get_height() - 70)
        self.grid.draw(screen, gridDrawRect, self.__selectedBlock__, self.__drawGridBorders__)

    def _get_grid_rect(self, screen_rect:pygame.Rect) -> pygame.Rect:
        return super()._offset_rect(screen_rect, pygame.Rect(0, 50, 0, -70))
    
    def _get_cell_at_screen_pos(self, screen_rect: pygame.Rect, click_pos: tuple[int, int]) -> tuple[int, int]:
        grid_rect: pygame.Rect = self._get_grid_rect(screen_rect)
        if not grid_rect.collidepoint(click_pos):
            return (-1, -1)
        
        cell_size: int = self.grid.get_cell_screen_size(screen_rect)
        grid_click_pos: tuple[int, int] = super()._offset_pos(click_pos, (grid_rect.left * -1, grid_rect.top * -1))
        clicked_cell: tuple[int, int] = (grid_click_pos[0] // cell_size, grid_click_pos[1] // cell_size)

        if clicked_cell[0] >= self.grid.width or clicked_cell[1] >= self.grid.height:
            return (-1, -1)
        
        return clicked_cell