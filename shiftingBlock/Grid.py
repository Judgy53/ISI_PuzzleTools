import random
from pygame import Color, Rect, Surface
import pygame
from shiftingBlock.Block import Block
from shiftingBlock.BlockShape import BlockShape

class Grid():
    def __init__(self, width: int, height: int, previous_grid: 'Grid | None' = None) -> None:
        self.width: int = width
        self.height: int = height
        self.blocks: dict[int, Block] = {}
        self.previous_grid: Grid | None = previous_grid

        self.__dirty_cache__: bool = True
        self.__cached_tile_grid__: list[list[int]] = self.get_cached_tile_grid()

    @staticmethod
    def from_tile_grid(tile_grid: list[list[int]], colors: dict[int, Color] | None = None) -> 'Grid | None':
        height: int = len(tile_grid)
        if height == 0:
            return None
        
        width: int = len(tile_grid[0])
        if width == 0 or not all(len(row) == width for row in tile_grid):
            return None
        
        if not colors:
            colors = {}
        
        grid: Grid = Grid(width, height)
        for y in range(height):
            for x in range(width):
                id: int = tile_grid[y][x]
                if id == -1:
                    continue
                if id not in grid.blocks:
                    color: pygame.Color = colors[id] if id in colors else pygame.Color(random.randint(0, 255), random.randint(0, 255),random.randint(0, 255))
                    grid.blocks[id] = Block(id, x, y, BlockShape([[True]]), color)
                else:
                    grid.blocks[id]._add_cell(x, y)
        grid.blocks = dict(sorted(grid.blocks.items()))
        grid.__dirty_cache__ = True  # Things were added manually, so force cache rebuilding
        return grid
    
    def get_cached_tile_grid(self) -> list[list[int]]:
        if not self.__dirty_cache__:
            return self.__cached_tile_grid__

        out: list[list[int]] = [[-1] * self.width for _ in range(self.height)]

        for id in self.blocks:
            block: Block = self.blocks[id]
            left = block.get_left()
            top = block.get_top()
            for y in range(block.shape.height):
                for x in range(block.shape.width):
                    if block.shape.is_cell_present(x, y):
                        out[top+y][left+x] = id

        self.__cached_tile_grid__ = out
        self.__dirty_cache__ = False
        
        return out

    def add_block(self, block:Block) -> None:
        self.__dirty_cache__ = True
        self.blocks[block.id] = block
        
    def add_block_if_legal(self, block:Block) -> bool:
        if self.does_block_fit(block) == True and self.does_block_intersects_any(block) == False:
            self.add_block(block)
            return True
        
        return False
    
    def does_block_fit(self, block:Block) -> bool:
        return (block.get_left() >= 0 and block.get_right() <= self.width and 
                block.get_top() >= 0 and block.get_bottom() <= self.height)
        
    def does_block_intersects_any(self, block:Block, ignore_id:int = -1) -> bool:
        cached_grid: list[list[int]] = self.get_cached_tile_grid()
        left = block.get_left()
        top = block.get_top()
        for y in range(block.shape.height):
            for x in range(block.shape.width):
                if not block.shape.is_cell_present(x, y):
                    continue
                cell:int = cached_grid[top+y][left+x]
                if cell != -1 and cell != ignore_id:
                    return True
        return False

        # for id, grid_block in self.blocks.items():
        #     if grid_block.intersects(block) and id != ignore_id:
        #         return True
        
        # return False
    
    def get_block_at_pos(self, x: int, y: int) -> Block | None:
        for id in self.blocks:
            if self.blocks[id].is_cell_present(x, y):
                return self.blocks[id]
        
        return None
    
    def get_all_legal_variants(self) -> list['Grid']:
        variant_grids: list[Grid] = []
        
        for id in self.blocks:
            variant_blocks: list[Block] = self.blocks[id].get_all_direct_variants()
            for vb in variant_blocks:
                if self.does_block_fit(vb) and not self.does_block_intersects_any(vb, id):
                    variant_grids.append(self._copy_with_replace_block(vb))

        return variant_grids
    
    def _copy_with_replace_block(self, replace_block: Block) -> 'Grid':
        copy: Grid = Grid(self.width, self.height, self)
        copy.blocks = self.blocks.copy()
        copy.add_block(replace_block)

        # for id, block in self.blocks.items():
        #     if id == replace_block.id:
        #         copy.add_block(replace_block)
        #     else:
        #         copy.add_block(block)
        #         # copy.add_block(block.copy())
        
        return copy
    
    def get_cell_screen_size(self, screen_rect: Rect) -> int:
        return min(screen_rect.width // self.width, screen_rect.height // self.height)
    
    def get_block_by_id(self, id: int) -> Block | None:
        if id in self.blocks:
            return self.blocks[id]
        
        return None
    
    def get_distance_from_goal(self, goal:'Grid') -> int:
        distance: int = 0

        for id in self.blocks:
            goal_block: Block | None = goal.get_block_by_id(id)
            if not goal_block:
                continue

            distance += abs(self.blocks[id].x - goal_block.x)
            distance += abs(self.blocks[id].y - goal_block.y)

        return distance

    def draw(self, screen: Surface, rect: Rect, highlight_block_index: int = -1, draw_grid_border: bool = True) -> None:
        cell_size: int = self.get_cell_screen_size(rect)
        for id, block in self.blocks.items():
            highlight: bool = highlight_block_index == id if highlight_block_index >= 0 else True
            
            block.draw(screen, rect.left, rect.top, cell_size, highlight)
            
        if draw_grid_border:
            border_color: Color = Color(255, 255, 255)
            for x in range(self.width):
                for y in range(self.height):
                    cell_rect: Rect = Rect(rect.left + x * cell_size, rect.top + y * cell_size, cell_size, cell_size)
                    pygame.draw.rect(screen, border_color, cell_rect, 1)

    def __hash__(self) -> int:
        return hash((self.width, self.height) + tuple(sorted(self.blocks.values(), key=lambda b: b.id)))