import pygame, sys
from pygame.locals import *

from breakout.context import BREAKOUT_CONTEXT as GAMEPLAY_CONTEXT
#
from context_manager import CONTEXT_MANAGER
from input_manager import INPUT_MANAGER
from xinput import MANAGER as GAMEPAD_MANAGER

pygame.init()

TARGET_FRAME_RATE = 30
frame_rate_counter = pygame.time.Clock()

SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600

# Initialize the display surface.
#
DISPLAY_SURFACE = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
DISPLAY_SURFACE.fill((255, 255, 255))
pygame.display.set_caption("Breakout 2024")
#
CONTEXT_MANAGER.display_surface = DISPLAY_SURFACE

# testing: start the game immediately
GAMEPLAY_CONTEXT.begin_play_session()
CONTEXT_MANAGER.enter_context(GAMEPLAY_CONTEXT)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            break

    time_delta : float = 1 / TARGET_FRAME_RATE

    GAMEPAD_MANAGER.update()
    INPUT_MANAGER.update(time_delta)
    CONTEXT_MANAGER.tick(time_delta)

    pygame.display.update()
    frame_rate_counter.tick(TARGET_FRAME_RATE)
