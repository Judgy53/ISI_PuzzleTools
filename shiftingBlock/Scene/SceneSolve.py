import heapq
import time
from typing import Any
from pygame import Rect, Surface
import pygame
from pygame.event import Event
from shiftingBlock.Grid import Grid
from shiftingBlock.PrioritizedGrid import PrioritizedGrid
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
        self.__to_visit__: list[PrioritizedGrid] = []
        self.__done__: bool = False

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
            prio_grid = self.get_next_prio_grid()
            if prio_grid.priority < 0:
                self.on_solve_fail()
                return
            elif prio_grid.priority == 0:
                self.on_solve_done(prio_grid.grid)
                return

            grid_hash: int = hash(prio_grid.grid)
            if grid_hash not in self.__visited__:
                self.add_new_variants(prio_grid.grid.get_all_legal_variants())
                self.__visited__.append(grid_hash)
            now = time.time()

    def add_new_variants(self, variants: list[Grid]) -> None:
        cached_time: float = time.time()
        for grid in variants:
            if hash(grid) not in self.__visited__:
                dist: int = grid.get_distance_from_goal(self.__goal_grid__)
                heapq.heappush(self.__to_visit__, PrioritizedGrid(dist, cached_time, grid))

    def get_next_prio_grid(self) -> PrioritizedGrid:
        if len(self.__to_visit__) <= 0:
            return PrioritizedGrid(-1, -1, Grid(0, 0))
        
        return heapq.heappop(self.__to_visit__)
    
    def draw(self, screen: Surface) -> None:
        Scene._draw_text_default_font(screen, 'Solving...', (10, 10))
        Scene._draw_text_default_font(screen, f'Visited: {len(self.__visited__)}', (10, 50))
        Scene._draw_text_default_font(screen, f'To Visit: {len(self.__to_visit__)}', (10, 90))
    
    def process_key_event(self, event: Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        
        match event.key:
            case pygame.K_ESCAPE:
                from shiftingBlock.Scene.SceneSetGoal import SceneSetGoal
                Scene._change_scene(SceneSetGoal, {'import': self.__import_data__})

    def process_mouse_event(self, _: Event, __: Rect) -> None:
        pass