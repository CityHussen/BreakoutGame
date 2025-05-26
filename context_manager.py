from typing import Optional
import pygame
from context import Context

class ContextManager:
    """Manages all active Contexts. See documentation on Context for details."""

    def __init__(self):
        self.active_contexts : list[Context]            = []
        self.display_surface : Optional[pygame.Surface] = None

        self.context_changed_last_frame     : bool  = False
        self.time_since_last_context_switch : float = 0

    @property
    def current_context(self) -> Optional[Context]:
        return self.active_contexts[-1]

    def enter_context(self, context:Context):
        """Enter the given context, if we aren't already in that context."""
        if context in self.active_contexts:
            return
        self.active_contexts.append(context)

    def exit_context(self, context:Context):
        """Attempt to exit the specified context."""
        self.active_contexts.remove(context)

    def tick(self, time_delta:float):
        """Run the process and render handlers for active contexts as is
        appropriate. Only the topmost ("current") context runs its process
        handler, and after that handler, we'll render all contexts that aren't
        covered by an opaque context, going from lowest to highest so that the
        current context draws overtop all the others."""
        if len(self.active_contexts) == 0:
            return
        con = self.current_context
        if con is not None:
            con.process(time_delta)
            self.context_changed_last_frame = con is not self.current_context
        else:
            self.context_changed_last_frame = False

        if self.context_changed_last_frame:
            self.time_since_last_context_switch = 0
        else:
            self.time_since_last_context_switch += time_delta

        if self.display_surface is not None:
            self.display_surface.fill((255, 255, 255))

            last_opaque : int = -1
            for i in range(len(self.active_contexts)):
                item = self.active_contexts[i]
                if item.is_opaque:
                    last_opaque = i
            for i in range(last_opaque, len(self.active_contexts)):
                item = self.active_contexts[i]
                item.render(self.display_surface)

CONTEXT_MANAGER = ContextManager()
