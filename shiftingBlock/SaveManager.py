from dataclasses import dataclass
import json
import os
import tkinter.filedialog
from typing import Any

from pygame import Color
from shiftingBlock.Grid import Grid

    
@dataclass
class ImportData:
    start_grid: Grid | None
    goal_grid: Grid | None
    solve_steps: list[Grid | None] | None


class SaveManager():
    @staticmethod
    def try_export(start_grid: Grid, goal_grid: Grid | None = None, steps: list[Grid] | None = None) -> bool:
        file = tkinter.filedialog.asksaveasfile(initialdir=os.getcwd(), confirmoverwrite=True, filetypes=[('grid', '.grid')], defaultextension='.grid')
        if not file:
            return False
        out_dict: dict[str, Any] = {'start_grid': start_grid.get_cached_tile_grid()}
        out_dict['colors'] = SaveManager.extract_grid_colors(start_grid)
        if goal_grid:
            out_dict['goal_grid'] = goal_grid.get_cached_tile_grid()
        if steps:
            out_dict['solve_steps'] = list(map(lambda g: g.get_cached_tile_grid(), steps))
        json.dump(out_dict, file)
        file.close()
        return True
    
    @staticmethod
    def try_import() -> ImportData | None:
        file = tkinter.filedialog.askopenfile(filetypes=[('grid', '.grid')], defaultextension='.grid')
        if not file:
            return None
        
        contents = json.load(file)
        if not isinstance(contents, dict) or 'start_grid' not in contents:
            return None
        
        colors: dict[int, Color] | None = SaveManager.import_grid_colors(contents['colors']) if 'colors' in contents else None
        start_grid: Grid | None = Grid.from_tile_grid(contents['start_grid'], colors)
        goal_grid: Grid | None = Grid.from_tile_grid(contents['goal_grid'], colors) if 'goal_grid' in contents else None
        solve_steps: list[Grid | None] | None = [Grid.from_tile_grid(t, colors) for t in contents['solve_steps']] if 'solve_steps' in contents else None
        if solve_steps:
            SaveManager.relink_solve_steps(solve_steps)
        
        return ImportData(start_grid, goal_grid, solve_steps)
    
    @staticmethod
    def extract_grid_colors(grid: Grid) -> dict[int, tuple[int, int, int, int]]:
        out: dict[int, tuple[int, int, int, int]] = {}
        for id in grid.blocks:
            color: Color = grid.blocks[id].color
            out[id] = (color.r, color.g, color.b, color.a)

        return out
    
    @staticmethod
    def import_grid_colors(import_colors: Any) -> dict[int, Color] | None:
        if not import_colors or not isinstance(import_colors, dict):
            return None
        
        if not all(isinstance(c, list) and len(c) == 4 for c in import_colors.values()):
            return None
        
        return {int(id): Color(c[0], c[1], c[2], c[3]) for id, c in import_colors.items()}
    
    @staticmethod
    def relink_solve_steps(solve_steps: list[Grid | None]) -> None:
        for i in range(1, len(solve_steps)):
            if step := solve_steps[i]:
                step.previous_grid = solve_steps[i-1]
