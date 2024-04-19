from pygame import Color, Surface
import pygame

class BlockShape():
    def __init__(self, cells: list[list[bool]]) -> None:
        self.cells: list[list[bool]] = cells
    
    @property
    def height(self) -> int:
        return len(self.cells)
    
    @property
    def width(self) -> int:
        return len(self.cells[0])

    def toggle_cell(self, x: int, y:int) -> None:
        (x, y) = self._ensure_room_for_new_cell(x, y)
        
        self.cells[y][x] = not self.cells[y][x]

    def _ensure_room_for_new_cell(self, x: int, y: int) -> tuple[int, int]:
        if x < 0:
            prepend_x: list[bool] = [False] * -x
            for i, row in enumerate(self.cells):
                self.cells[i] = prepend_x + row
            x = 0
        elif x >= self.width:
            append_x: list[bool] = [False] * (x - self.width + 1)
            for i, row in enumerate(self.cells):
                self.cells[i] = row + append_x

        if y < 0:
            prepend_y: list[list[bool]] = [[False] * self.width] * -y
            self.cells = prepend_y + self.cells
            y = 0
        elif y >= self.height:
            append_y: list[list[bool]] = [[False] * self.width] * (y - self.height + 1)
            self.cells = self.cells + append_y

        return (x, y)
    
    def trim(self) -> tuple[int, int]:
        trimmed_columns_left: int = 0
        trimmed_rows_top: int = 0

        # trim top
        while all(cell == False for cell in self.cells[0]):
            trimmed_rows_top += 1
            self.cells.pop(0)

        # trim bottom
        while all(cell == False for cell in self.cells[self.height - 1]):
            self.cells.pop()

        # trim left
        while all(row[0] == False for row in self.cells):
            trimmed_columns_left += 1
            for row in self.cells:
                row.pop(0)

        # trim right
        while all(row[self.width - 1] == False for row in self.cells):
            for row in self.cells:
                row.pop()

        return (trimmed_columns_left, trimmed_rows_top)
            

    def is_cell_present(self, x: int, y: int) -> bool:
        if not self.is_valid_pos(x, y):
            return False
        
        return self.cells[y][x]
    
    def cell_count(self) -> int:
        return sum(row.count(True) for row in self.cells)
    
    def is_single_segment(self) -> bool:
        for y in range(self.height):
            for x in range(self.width):
                if self.cells[y][x] == True:
                    visited: list[tuple[int, int]] = self._try_visit_all(x, y, [])
                    return self.cell_count() == len(visited)
        return False
    
    def _try_visit_all(self, x: int, y: int, visited: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if (x, y) in visited or not self.is_cell_present(x, y):
            return visited
        
        visited.append((x, y))

        self._try_visit_all(x + 1, y, visited)
        self._try_visit_all(x - 1, y, visited)
        self._try_visit_all(x, y + 1, visited)
        self._try_visit_all(x, y - 1, visited)

        return visited
    
    def is_valid_pos(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height
    
    def copy(self) -> 'BlockShape':
        return BlockShape([row.copy() for row in self.cells])
    
    def draw(self, surface: Surface, block_x: int, block_y: int, cell_size: int, color:Color) -> None:
        for y in range(self.height):
            for x in range(self.width):
                cellVal: bool = self.cells[y][x]
                if not cellVal:
                    continue
                
                rect: pygame.Rect = pygame.Rect(block_x + x * cell_size, block_y + y * cell_size, cell_size, cell_size)
                surface.fill(color, rect, special_flags=pygame.BLEND_RGBA_ADD)

    def __hash__(self) -> int:
        return hash(tuple(map(tuple, self.cells)))