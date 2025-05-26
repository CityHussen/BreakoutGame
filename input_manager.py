from enum import Enum
from typing import Optional
import pygame
from context_manager import CONTEXT_MANAGER, Context
from geom import Vec2
from xinput import Gamepad, Button as GamepadButton, MANAGER as GAMEPAD_MANAGER

class Device(Enum):
    NONE     = 0
    KEYBOARD = 1
    MOUSE    = 2
    GAMEPAD  = 3

class ButtonState(Enum):
    UP          = 0
    DOWN        = 1 # Button was pressed down on this frame
    HELD        = 2 # Button is being held
    AUTO_REPEAT = 3 # Button is being held and the auto-repeat interval is met

KEY_REPEAT_INTERVAL = 0.030 # seconds

_ALL_PYGAME_KEYS = []
for _name in pygame.locals.__all__:
    if isinstance(_name, str) and _name.startswith("K_"):
        _ALL_PYGAME_KEYS.append(pygame.__dict__[_name])

class InputActionStates:
    """Map current inputs to "semantic" actions, such that inputs from multiple
    devices at once don't double up or confuse the program."""
    def __init__(self):
        self.last_keynav_device : Device = Device.NONE

        # arrow key and joystick inputs, normalized
        self.directional_move : Vec2 = Vec2()

        # gamepad right stick
        self.directional_alt  : Vec2 = Vec2()

        #
        # Gameplay states
        #
        self.serve_ball : ButtonState = ButtonState.UP

        #
        # UI states
        #
        self.ui_toggle_pause : ButtonState = ButtonState.UP
        self.ui_activate     : ButtonState = ButtonState.UP # Space/XInput A
        self.ui_cancel       : ButtonState = ButtonState.UP # Esc/XInput B
        self.ui_page_up      : ButtonState = ButtonState.UP
        self.ui_page_down    : ButtonState = ButtonState.UP
        #
        self.ui_navigate_up    : ButtonState = ButtonState.UP
        self.ui_navigate_down  : ButtonState = ButtonState.UP
        self.ui_navigate_left  : ButtonState = ButtonState.UP
        self.ui_navigate_right : ButtonState = ButtonState.UP

    def normalize(self):
        """Correct any unusual inputs."""
        if self.directional_move.length() > 1:
            self.directional_move.normalize()
        if self.directional_alt.length() > 1:
            self.directional_alt.normalize()

    def any_active(self) -> bool:
        if not self.directional_move.is_zero():
            return True
        if not self.directional_alt.is_zero():
            return True

        non_repeatable_buttons = [
            self.serve_ball,
            self.ui_toggle_pause,
            self.ui_activate,
            self.ui_cancel,
            self.ui_page_up,
            self.ui_page_down,
        ]
        for button in non_repeatable_buttons:
            if button == ButtonState.DOWN:
                return True

        repeatable_buttons = [
            self.ui_navigate_up,
            self.ui_navigate_down,
            self.ui_navigate_left,
            self.ui_navigate_right,
        ]
        for button in repeatable_buttons:
            if button in (ButtonState.DOWN, ButtonState.AUTO_REPEAT):
                return True

        return False

    def reset(self):
        """Reset input state, but not input "memory" such as the current input
        context or the last-used device."""
        self.directional_move.x = 0
        self.directional_move.y = 0
        self.directional_alt.x  = 0
        self.directional_alt.y  = 0

        self.serve_ball = ButtonState.UP

        self.ui_toggle_pause = ButtonState.UP
        self.ui_activate     = ButtonState.UP
        self.ui_cancel       = ButtonState.UP
        self.ui_page_up      = ButtonState.UP
        self.ui_page_down    = ButtonState.UP
        #
        self.ui_navigate_up    = ButtonState.UP
        self.ui_navigate_down  = ButtonState.UP
        self.ui_navigate_left  = ButtonState.UP
        self.ui_navigate_right = ButtonState.UP

class InputManager:
    """Takes raw inputs from hardware (e.g. keypresses, gamepad inputs) and
    stores them as "semantic" inputs (e.g. Press Start -> Press Pause)."""
    def __init__(self):
        self.state = InputActionStates()

        self._last_pressed_keys = None
        self._ignored_keys      = []

    def _ignore_all_currently_pressed_keyboard_keys(self):
        pressed_keys = pygame.key.get_pressed()
        for key in _ALL_PYGAME_KEYS:
            if pressed_keys[key]:
                self._ignored_keys.append(key)

    def _stop_ignoring_released_keyboard_keys(self):
        pressed_keys = pygame.key.get_pressed()

        released = []
        for key in self._ignored_keys:
            if not pressed_keys[key]:
                released.append(key)
        self._ignored_keys = [e for e in self._ignored_keys if e not in released]

    def _update_input_ignore_states(self):
        #
        # If the context changes, then ignore any gamepad buttons that are
        # currently down, until such time as they are released. This will
        # prevent button presses from "bleeding into" newly-opened menus (or
        # "bleeding out of" newly-closed ones).
        #
        if not CONTEXT_MANAGER.context_changed_last_frame:
            self._stop_ignoring_released_keyboard_keys()
            #
            # No need to manage un-ignoring gamepad buttons; the GAMEPAD_MANAGER
            # does that for us.
            #
            return

        self._ignore_all_currently_pressed_keyboard_keys()

        if GAMEPAD_MANAGER.supported:
            for gamepad in GAMEPAD_MANAGER.gamepads:
                if not gamepad.connected:
                    continue
                gamepad.ignore_all_currently_down_buttons()

    def _update_state_by_keyboard(self):
        if not pygame.key.get_focused():
            return

        pressed_keys = pygame.key.get_pressed()
        pressed_mods = pygame.key.get_mods()

        context = CONTEXT_MANAGER.current_context
        is_in_menu = False
        if context is not None:
            is_in_menu = context.is_menu

        dir_move_keys: Vec2 = self.state.directional_move

        if pressed_keys[pygame.K_w] or pressed_keys[pygame.K_UP]:
            dir_move_keys.y -= 1
        if pressed_keys[pygame.K_s] or pressed_keys[pygame.K_DOWN]:
            dir_move_keys.y += 1
        if pressed_keys[pygame.K_a] or pressed_keys[pygame.K_LEFT]:
            dir_move_keys.x -= 1
        if pressed_keys[pygame.K_d] or pressed_keys[pygame.K_RIGHT]:
            dir_move_keys.x += 1

        def _state_of(key:int):
            if not pressed_keys[key]:
                return ButtonState.UP
            if self._last_pressed_keys is not None:
                if self._last_pressed_keys[key]:
                    return ButtonState.HELD
            return ButtonState.DOWN

        if not is_in_menu:
            self.state.ui_toggle_pause = _state_of(pygame.K_ESCAPE)
            self.state.serve_ball      = _state_of(pygame.K_SPACE)
        else:
            self.state.ui_activate  = _state_of(pygame.K_SPACE)
            self.state.ui_cancel    = _state_of(pygame.K_ESCAPE)
            self.state.ui_page_up   = _state_of(pygame.K_PAGEUP)
            self.state.ui_page_down = _state_of(pygame.K_PAGEDOWN)

            self.state.ui_navigate_up    = _state_of(pygame.K_UP)
            self.state.ui_navigate_down  = _state_of(pygame.K_DOWN)
            self.state.ui_navigate_left  = _state_of(pygame.K_LEFT)
            self.state.ui_navigate_right = _state_of(pygame.K_RIGHT)

        self.state.normalize()
        self._last_pressed_keys = pressed_keys

    def _update_state_by_gamepad(self, gamepad:Gamepad):
        if not pygame.key.get_focused():
            return

        context = CONTEXT_MANAGER.current_context
        is_in_menu = False
        if context is not None:
            is_in_menu = context.is_menu

        dir_move : Vec2 = gamepad.left_stick

        if gamepad.is_button_down(GamepadButton.DPAD_UP):
            dir_move.y -= 1
        if gamepad.is_button_down(GamepadButton.DPAD_DOWN):
            dir_move.y += 1
        if gamepad.is_button_down(GamepadButton.DPAD_LEFT):
            dir_move.x -= 1
        if gamepad.is_button_down(GamepadButton.DPAD_RIGHT):
            dir_move.x += 1

        self.state.directional_move = dir_move

        def _state_of(button:GamepadButton):
            if not gamepad.is_button_down(button):
                return ButtonState.UP
            if gamepad.button_pressed_now(button):
                return ButtonState.DOWN
            return ButtonState.HELD

        if not is_in_menu:
            self.state.ui_toggle_pause = _state_of(GamepadButton.START)
            self.state.serve_ball      = _state_of(GamepadButton.A)
        else:
            self.state.ui_activate  = _state_of(GamepadButton.A)
            self.state.ui_cancel    = _state_of(GamepadButton.B)
            self.state.ui_page_up   = _state_of(GamepadButton.LT)
            self.state.ui_page_down = _state_of(GamepadButton.RT)

    def _finalize_state_from_gamepads(self):
        """After we've gathered input from all gamepads, use this function to
        coalesce it."""
        dir_move = self.state.directional_move

        if dir_move.y < 0:
            self.state.ui_navigate_down = ButtonState.UP
            if self.state.ui_navigate_up != ButtonState.UP:
                self.state.ui_navigate_up = ButtonState.HELD
            else:
                self.state.ui_navigate_up = ButtonState.DOWN
        elif dir_move.y > 0:
            self.state.ui_navigate_up = ButtonState.UP
            if self.state.ui_navigate_down != ButtonState.UP:
                self.state.ui_navigate_down = ButtonState.HELD
            else:
                self.state.ui_navigate_down = ButtonState.DOWN

        if dir_move.x < 0:
            self.state.ui_navigate_right = ButtonState.UP
            if self.state.ui_navigate_left != ButtonState.UP:
                self.state.ui_navigate_left = ButtonState.HELD
            else:
                self.state.ui_navigate_left = ButtonState.DOWN
        elif dir_move.x > 0:
            self.state.ui_navigate_left = ButtonState.UP
            if self.state.ui_navigate_right != ButtonState.UP:
                self.state.ui_navigate_right = ButtonState.HELD
            else:
                self.state.ui_navigate_right = ButtonState.DOWN

    def update(self, time_delta:float):
        self.state.reset()
        self._update_input_ignore_states()

        gamepad_used = False
        if GAMEPAD_MANAGER.supported:
            for gamepad in GAMEPAD_MANAGER.gamepads:
                if not gamepad.connected:
                    continue
                if gamepad.any_inputs_being_made():
                    gamepad_used = True
                    self.state.last_keynav_device = Device.GAMEPAD
                    #
                    # We'll aggregate inputs from all gamepads. They'll be
                    # normalized at the end of the process.
                    #
                    self._update_state_by_gamepad(gamepad)

                    # TODO: Currently, `_update_state_by_gamepad` fails to
                    #       aggregate buttons: we only store the buttons for the
                    #       last gamepad we processed. For now, I'm throwing a
                    #       `break` statement in here so that things work at all
                    #       but I need to redo how we store those values (and
                    #       then deal with them further in the "finalize" func)
                    #       so we can remove this `break` and actually coalesce
                    #       input across all gamepads as planned
                    break

        if not gamepad_used:
            self._update_state_by_keyboard()
            if self.state.any_active():
                self.state.last_keynav_device = Device.KEYBOARD

        self.state.normalize()
        if gamepad_used:
            self._finalize_state_from_gamepads()

INPUT_MANAGER = InputManager()
