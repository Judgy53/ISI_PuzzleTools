from typing import Any
from pygame import Surface
import pygame
from pygame.event import Event
from abc import ABCMeta, abstractmethod

from shiftingBlock import CustomEvents

class Scene(metaclass=ABCMeta):
    __default_font__: pygame.font.Font | None = None
    
    def __init__(self, data:dict[str, Any] = {}) -> None:
        self.initialize(data)
    
    @staticmethod
    def _draw_text_default_font(screen: Surface, text: str, position: tuple[int, int], font_size: int | None = None, color: pygame.Color = pygame.Color(255, 255, 255)) -> None:
        if not Scene.__default_font__:
            Scene.__default_font__ = pygame.font.SysFont("arial", 30)

        font: pygame.font.Font = pygame.font.SysFont("arial", font_size) if font_size else Scene.__default_font__

        Scene._draw_text(screen, text, position, font, color)
    
    @staticmethod
    def _draw_text(screen: Surface, text:str, position: tuple[int, int], font:pygame.font.Font, color: pygame.Color = pygame.Color(255, 255, 255)):
        renderedSurface: Surface = font.render(text, True, color)
        screen.blit(renderedSurface, position)

    @staticmethod
    def _change_scene(scene: type, data: dict[str, Any] = {}):
        if not issubclass(scene, Scene):
            raise TypeError('new scene needs to be a subclass of scene')
        event: pygame.event.Event = pygame.event.Event(CustomEvents.CHANGE_SCENE, scene=scene, data=data)
        pygame.event.post(event)

    @staticmethod
    def _offset_rect(r1: pygame.Rect, r2: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(r1.x + r2.x, r1.y + r2.y, r1.width + r2.width, r1.height + r2.height)
    
    @staticmethod
    def _offset_pos(p1: tuple[int, int], p2: tuple[int, int]) -> tuple[int, int]:
        return (p1[0] + p2[0], p1[1] + p2[1])

    @abstractmethod
    def initialize(self, data: dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def update(self) -> None:
        pass
    
    @abstractmethod
    def draw(self, screen:Surface) -> None:
        pass
        
    def process_key_event(self, _:Event) -> None:
        pass

    def process_mouse_event(self, _:Event, __: pygame.Rect) -> None:
        pass