from typing import Any
import pygame
from shiftingBlock import CustomEvents
from shiftingBlock.Scene.Scene import Scene
from shiftingBlock.Scene.SceneCreateGrid import SceneCreateGrid
# from shiftingBlock.Scene.SceneSolve import SceneSolve
# import cProfile, pstats, io
# from pstats import SortKey


class ShiftingBlockApp():
    
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
    
        self.__screen__ = pygame.display.set_mode((700, 500), pygame.RESIZABLE)
    
        self.__running__ = False
        self.__clock__ = pygame.time.Clock()
        self.__draw_FPS__ = True

        # self.__profiler_s__: io.StringIO = io.StringIO()
        # self.__profiler_ps__: pstats.Stats = pstats.Stats(stream=self.__profiler_s__)
        # self.__profiler_hit_count__: int = 0

        self.change_scene(SceneCreateGrid)

    def run(self) -> None:
        self.__running__ = True
        while self.__running__:
            self.process_events()
            self.update()
            self.draw()
            self.__clock__.tick(60)
        
        pygame.quit()
            
    def process_events(self) -> None:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.__running__ = False
                case pygame.VIDEORESIZE:
                    self.__screen__ = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                case CustomEvents.CHANGE_SCENE:
                    self.change_scene(event.scene, event.data)
                case pygame.KEYDOWN | pygame.KEYUP:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_F6:
                        self.__draw_FPS__ = not self.__draw_FPS__
                    self.__current_scene__.process_key_event(event)
                case pygame.MOUSEBUTTONDOWN | pygame.MOUSEBUTTONUP | pygame.MOUSEMOTION:
                    self.__current_scene__.process_mouse_event(event, self.__screen__.get_rect())

    def update(self) -> None:
        # if isinstance(self.__current_scene__, SceneSolve):
        #     pr = cProfile.Profile()
        #     pr.enable()
        #     self.__current_scene__.update()
        #     pr.disable()
        #     self.__profiler_ps__.add(pr)

        #     self.__profiler_hit_count__ += 1
        #     if self.__profiler_hit_count__ >= 50:
        #         self.__profiler_ps__.sort_stats(SortKey.CUMULATIVE)
        #         self.__profiler_ps__.print_stats()
        #         print(self.__profiler_s__.getvalue())
        #         self.__profiler_hit_count__ = 0
        # else:
        #     self.__current_scene__.update()
        self.__current_scene__.update()

    def draw(self) -> None:
        self.__screen__.fill(pygame.Color(0, 0, 0))
        self.__current_scene__.draw(self.__screen__)

        if self.__draw_FPS__:
            Scene._draw_text_default_font(self.__screen__, f'FPS:{round(self.__clock__.get_fps(), 1)}', (self.__screen__.get_width() - 90, 5), 20, pygame.Color(0, 255, 0))
        pygame.display.flip()

    def change_scene(self, scene:type, data: dict[str, Any] = {}) -> None:
        if isinstance(scene, type) and issubclass(scene, Scene):
            self.__current_scene__ = scene(data)
        else:
            raise TypeError("scene is not a subtype of Scene")