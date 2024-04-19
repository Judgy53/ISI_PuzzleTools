from pygame import Color, Surface
from shiftingBlock.BlockShape import BlockShape


class Block():
    def __init__(self, id: int, x: int, y: int, shape: BlockShape, color:Color) -> None:
        self.id: int = id
        self.x: int = x
        self.y: int = y
        self.shape: BlockShape = shape
        self.color: Color = color
        
    def get_left(self) -> int:
        return self.x
    
    def get_right(self) -> int:
        return self.x + self.shape.width
    
    def get_top(self) -> int:
        return self.y
    
    def get_bottom(self) -> int:
        return self.y + self.shape.height
    
    def is_cell_present(self, x: int, y: int) -> bool:
        return self.shape.is_cell_present(x - self.get_left(), y - self.get_top())
    
    def try_add_cell(self, x: int, y: int) -> bool:
        if self.is_cell_present(x, y):
            return False

        if (self.is_cell_present(x - 1, y)
            or self.is_cell_present(x + 1, y)
            or self.is_cell_present(x, y - 1)
            or self.is_cell_present(x, y + 1)):
            self._add_cell(x, y)
            return True
        
        return False
    
    def _add_cell(self, x:int, y:int) -> None:
        self.shape.toggle_cell(x - self.get_left(), y - self.get_top())

        if x < self.get_left():
            self.x -= 1

        if y < self.get_top():
            self.y -= 1

    def try_remove_cell(self, x:int, y:int) -> bool:
        if self.is_cell_present(x, y) and self.shape.cell_count() > 1:
            self.shape.toggle_cell(x - self.get_left(), y - self.get_top())
            (trimmed_columns_left, trimmed_rows_top) = self.shape.trim()
            if not self.shape.is_single_segment():
                self.shape.toggle_cell(x - self.get_left(), y - self.get_top())
                return False
            self.x += trimmed_columns_left
            self.y += trimmed_rows_top
            return True
        return False
    
    def intersects(self, other: 'Block') -> bool:
        # Check if there's any overlap in X axis
        if self.get_right() <= other.get_left() or self.get_left() >= other.get_right():
            return False
        
        # Check if there's any overlap in Y axis
        if self.get_bottom() <= other.get_top() or self.get_top() >= other.get_bottom():
            return False
        
        overlapLeft: int = max(self.get_left(), other.get_left())
        overlapRight: int = min(self.get_right(), other.get_right())
        overlapTop: int = max(self.get_top(), other.get_top())
        overlapBottom: int = min(self.get_bottom(), other.get_bottom())
        
        for y in range(overlapTop, overlapBottom):
            for x in range(overlapLeft, overlapRight):
                #print(f"{x}:{y} = {self.isCellPresent(x, y)} and {other.isCellPresent(x, y)}")
                if self.is_cell_present(x, y) and other.is_cell_present(x, y):
                    return True
        
        return False
    
    def get_all_direct_variants(self) -> list['Block']:
        variant_dirs: list[tuple[int, int]] = [(1, 0), (0, 1)]
        if self.get_left() > 0:
            variant_dirs.append((-1, 0))
        if self.get_top() > 0:
            variant_dirs.append((0, -1))

        variant_blocks: list[Block] = []

        for shift_x, shift_y in variant_dirs:
            variant_blocks.append(self.copy_and_shift(shift_x, shift_y))

        return variant_blocks
    
    def copy(self) -> 'Block':
        return Block(self.id, self.x, self.y, self.shape.copy(), self.color)
    
    def copy_and_shift(self, shift_x: int, shift_y: int) -> 'Block':
        return Block(self.id, self.x + shift_x, self.y + shift_y, self.shape.copy(), self.color)
        
    def draw(self, surface:Surface, gridX: int, gridY: int, cell_size: int, is_selected: bool) -> None:
        color: Color = self.color if is_selected else self.color.grayscale()
        self.shape.draw(surface, gridX + self.x * cell_size, gridY + self.y * cell_size, cell_size, color)

    def __hash__(self) -> int:
        return hash((self.id, self.x, self.y, self.shape))