import time
from typing import Any

from pygame import Rect, Surface
import pygame
from pygame.event import Event
from shiftingBlock.Grid import Grid
from shiftingBlock.SaveManager import ImportData
from shiftingBlock.Scene.Scene import Scene
from shiftingBlock.Scene.SceneResultsSuccess import SceneResultsSuccess


class SceneSolve(Scene):

    def initialize(self, data: dict[str, Any]) -> None:
        if not 'import' in data or not isinstance(data['import'], ImportData):
            raise ValueError('import not in data')
        self.__import_data__: ImportData = data['import']

        if 'use_previous_solve' in data and data['use_previous_solve'] and data['import'].solve_steps:
            if last_step := data['import'].solve_steps[-1]:
                self.on_solve_done(last_step)

        if not data['import'].start_grid:
            raise ValueError('start_grid not in data')
        
        if not data['import'].goal_grid:
            raise ValueError('goal_grid not in data')
        
        self.__start_grid__: Grid = data['import'].start_grid
        self.__goal_grid__: Grid = data['import'].goal_grid
        self.__visited__: list[int] = []
        self.__to_visit__: dict[int, list[Grid]] = dict()
        self.__done__: bool = False

        for i in range(self.__start_grid__.width + self.__start_grid__.height):
            self.__to_visit__.setdefault(i, [])

        self.add_new_variants([self.__start_grid__])

    def on_solve_done(self, grid: Grid) -> None:
        self.__done__ = True
        Scene._change_scene(SceneResultsSuccess, data={'import': self.__import_data__, 'grid_solved': grid})

    def on_solve_fail(self) -> None:
        raise NotImplementedError('solve failed')

    def update(self) -> None:
        start_time: float = time.time()
        now: float = time.time()

        while now - start_time < 0.15 and not self.__done__:
            next_grid, grid_dist = self.get_next_grid_and_dist()
            if grid_dist < 0:
                self.on_solve_fail()
                return
            elif grid_dist == 0:
                self.on_solve_done(next_grid)
                return
            
            self.__to_visit__[grid_dist].remove(next_grid)

            next_hash: int = hash(next_grid)
            if next_hash not in self.__visited__:
                self.add_new_variants(next_grid.get_all_legal_variants())
                self.__visited__.append(next_hash)
            now = time.time()

    def add_new_variants(self, variants: list[Grid]) -> None:
        for grid in variants:
            if hash(grid) not in self.__visited__:
                dist: int = grid.get_distance_from_goal(self.__goal_grid__)
                self.__to_visit__[dist].append(grid)

    def get_next_grid_and_dist(self) -> tuple[Grid, int]:
        # min_grid: Grid = self.__to_visit__[0]
        # min_dist: int = min_grid.get_distance_from_goal(self.__goal_grid__)

        # for index in range(1, len(self.__to_visit__)):
        #     grid: Grid = self.__to_visit__[index]
        #     dist: int = grid.get_distance_from_goal(self.__goal_grid__)

        #     if dist < min_dist:
        #         min_dist = dist
        #         min_grid = grid
        min_dist: int = -1
        for (dist, list_grid) in self.__to_visit__.items():
            if min_dist != -1 and dist >= min_dist:
                continue
            if len(list_grid) > 0:
                min_dist = dist

        if min_dist == -1:
            return (Grid(0, 0), -1) 

        return (self.__to_visit__[min_dist][0], min_dist)
    
    def count_to_visit_length(self) -> int:
        length: int = 0
        for val in self.__to_visit__.values():
            length += len(val)
        
        return length
    
    def draw(self, screen: Surface) -> None:
        Scene._draw_text_default_font(screen, 'Solving...', (10, 10))
        Scene._draw_text_default_font(screen, f'Visited: {len(self.__visited__)}', (10, 50))
        Scene._draw_text_default_font(screen, f'To Visit: {self.count_to_visit_length()}', (10, 90))
    
    def process_key_event(self, event: Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        
        match event.key:
            case pygame.K_ESCAPE:
                from shiftingBlock.Scene.SceneSetGoal import SceneSetGoal
                Scene._change_scene(SceneSetGoal, {'import': self.__import_data__})

    def process_mouse_event(self, _: Event, __: Rect) -> None:
        pass