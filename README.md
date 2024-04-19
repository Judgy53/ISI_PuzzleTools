# ISI_PuzzleTools

Python app to help solve various puzzle types for Islands of Insight. Only `Shifting Mosaics` is supported for now.

## How to run
Requires python3 and pygame. Command to run : `python .\main.py`

## Shifting Mosaics
Create the grid, set the goal and it will try to solve it. It does so via `smart bruteforce` : testing all combinations making sure it ignores already seen cases, prioritizes closest to goal.

How to interact with all the scenes :
- In most scenes, `e` to export the grid, `i` to import one. `Enter` to go to next scene.
- **Create Grid**: Set the size of the grid.
  - `Left` and `Right` Arrow to change the width.
  - `Up` and `Down` Arrow to change the height.
- **Fill Grid**: Fill the starting grid by creating blocks.
  - `Click` on a cell to toggle its state for the current block (all cells must be connected, must have at least 1 cell)
  - `Left` and `Right` Arrow to change currently selected block.
  - `Del` to delete currently selected block.
- **Set Goal**: Create the end goal.
  - `Click` on a cell to position the currently selected block on the goal grid. `Click` on the block again to remove it from the goal.
  - `Left` and `Right` Arrow to change currently selected block.
  - `Ctrl+Enter` will skip the solve and show previously found solution (if rerunning the same one or imported from file)
- **Solve**: Let the app do its magic.
  - `Escape` to cancel the solve and go back to previous scene.
  - If no solution is found, app will crash because I'm lazy.
- **Results**: Show the steps to solve.
  - `Left` and `Right` Arrow to change currently shown step.
  - `Enter` to go back to `Fill Grid` scene.
 
## Contributing
All the code was written using `mypy` syntax checker. I'd like to keep it, but won't be cancel your PR if you don't want to use it.

Most of the code is uncommented and undocumented. The project was meant to be a small one, and I have been too lazy to go back and clean it.

## Todo
- Improve solve speed (MultiThreading ?).
- Improve export file size (only export block movement instead of whole grid each step)
- Improve usability (show keybinds, proper UI with clickable buttons)
- Export to exe for easier use for non developers.
