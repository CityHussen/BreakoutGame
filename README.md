
## Tasks

### Critical

These are the tasks we should try the hardest to have finished by the end of Week 4.

* Input handling
  * Ability to control the paddle using the mouse
    * See bullet points below for general notes on handling mouse input 
    * Once this is implemented, modify the "serve ball" text banner code so that when the player's last input is a mouse input, we show "LEFT-CLICK TO SERVE THE BALL". We already have code to swap the text in real-time between keyboard and gamepad prompts.
  * Mouse support in general
    * Input manager needs to be able to track mouse movement, but only when the window has focus and the mouse passes above it.
      * Might be good for the input manager to just have a general "should we care about the mouse right now?" bool that the various `Context`s can check.
    * If the window doesn't have focus, and the user focuses it by clicking on it, then that particular mousedown should be ignored until the mouse button is released. (That is: the user probably won't have the button down for just a single frame; they'll likely have the button physically pressed down for a few frames at a time. Even if on frame 1 of the user's mouse click, we don't "see" the mouse being clicked because we're regaining window focus, we want to make sure that on frame 2, we don't blindly react to the mouse button being down. We should only react to clicks (mousedown and mouseup) that begin while we already have window focus.)
* Menus
  * Main menu
    * Button to start playing
    * Button to access high scores
  * Pause menu
  * High score listing
  * High score entry
* Game config file
* High score entry and storage

### Less critical

These are the kinds of tasks we'll want to look into having done by Week 6.

* Better graphics
  * `_TextBanner` in `breakout\context.py` could be improved. Currently, we draw text and the text background one word at a time. The problem is that due to how `pygame.freetype.Font` calculates text metrics, the `Rect`s for each word don't always have consistent heights, which means that when we draw the background color for text, the top or bottom edges may not line up from word to word. We could solve this if we had `FontStamp` divide its stored words by line (i.e. define a `_Line` helper class) and draw the fill boxes per-line.
  
    `FontStamp` already has to consider lines anyway as part of the word-wrapping it does in its `compute` step. All we'd really have to do is just *store* the text as lines instead of storing it word-by-word. A nice benefit of this is that we could then store just a y-value per line rather than per-word, though we'd still have to remember to apply each word's `rect.y` when drawing the text.
  * Can we modify `_TextBanner` and `FontStamp` to have better control over line spacing? We use the computation recommended by pygame's documentation, but the resulting line spacing is a bit too large for my tastes. It'd be nice if we had just enough spacing to prevent lines from overlapping, with the ability to then specify additional spacing as desired.
    * We currently use `get_sized_height()`. By contast, I believe CSS treats the line box height as the `ascender` plus the `descender` or something like that. 
    * Honestly, `FontStamp` is pretty janky in practice, especially when trying to position a line box within a container. I think it's currently treating the Y-coordinate for its `draw` method as the text baseline? If we have it store its contents by line box, then it might be easier to control some of the math involved. 
* Graphical effects
  * Ball should have some sort of particle effect e.g. trailing fire whenever it's in a "destructive" state. This will make it obvious that when the ball fails to destroy a block, that's deliberate -- and it'll allow players to more easily intuit when the ball becomes destructive. 
  * When a non-destructive ball hits a block, it'd be nice to have dust particles or something similar puff off of the block's surface.
  * When a ball destroys a block, it'd be nice to have VFX for the block crumbling or breaking apart.
  * When a ball falls into the pit and is destroyed, it'd be nice to have some sort of VFX for the ball's destruction. In the *Super Smash Bros.* series, there's a bright "blast" effect for when players are knocked out of the level and into the "blast zone;" that might be a fun thing to imitate.
  * Wonder if we can have the sides of the paddle crumble when the paddle grows narrower as part of difficulty progression?
* Investigate alternative options for decoupling "logical sizes" from "display sizes," so we can use logical sizes that make more sense than our current ones.
  * We could use `cairo` to programmatically draw our graphics. The problem with this is that if we aim for e.g. pixel-perfect/nearest-neighbor graphics, then we might see "size jitter" where if an object is positioned on sub-pixel boundaries, its size appears to change by one pixel as it moves and rounding errors appear and disappear.
  * What if we took the CSS approach? "Responsive design" basically involves designing your site for full-size monitors, and then using `@media` queries to change your layout for different screen/viewport widths. What if we just did something similar for Breakout? We could draw paddle, ball, and block graphics at varying "key sizes;" then, we'd have the game figure out which "key size" is nearest to the final display resolution, and then render based on that.
    * For key sizes, could hand-pixel the smallest ones and then use SVGs for larger sizes, with GIMP or another image editor used to render out those SVGs at varying dimensions. 
    * **Thinking this approach might be a good way to go. In fact, this seems ideal even if we don't change logical sizes and we just persist with the weird 1844x2397 playing field.**
* Sound effects
  * On ball/block collision (block destroyed)
  * On ball/paddle collision
  * On ball/inert collision (playing field edge, or block if not destroyed)
  * On ball destroyed
  * On ball served
  * On ball sped up
  * On paddle narrowed
  * *I've experimented with trying to make some simple retro-style sounds using noise, square, and saw waves, but it's hard to find a robust online editor. RGMEx's in-browser Pokemon GBC cry editor is ironically the closest thing to usable, and I've gotten a couple good rumble/impact sounds out of it, but even that doesn't give a lot of control and isn't very intuitive. Maybe I'll spend Week 5, the "not programming Breakout" week, looking into making my own waveform editor... Or maybe I should just go look for free sounds under Creative Commons and Public Domain licensing...*
* Music
  * I am *not* a composer. Maybe I can find a free DAW with retro/chiptune-style instruments, though? Or maybe some Kevin MacLeod tracks will do, with credit as per the licensing of course.
* Light gamepad vibrations when the ball hits the paddle? We wrap XInput directly, but I haven't exposed `XInputSetState` (which, despite its very vague name, only handles vibrations, and is the only place *to* handle them) to Python yet.
  * We'd want to design this API in such a manner that callers would specify a vibration intensity and duration. We'd want to have `_XInputManager.update` take a time delta and use that to halt vibrations once their durations have elapsed. Ideally, if two vibrations overlap (e.g. queueing a new one while an old one is still playing), we'd aggregate them together (i.e. `max()` the intensities of all ongoing vibrations and pass that to XInput). We'd also want to rig it up so that if the current `Context` changes after a vibration begins, the vibration is halted instantly (so that if you pause, etc., gameplay vibrations don't persist into menus or worse, get stuck).
    * If we wanna go the extra mile, we could even make it possible to specify an easing function for a vibration as well.
* Input manager
  * Can we get auto-repeating keys implemented? We don't *need* them, strictly speaking, for most of our planned UI designs, but they'll make navigating through lists (e.g. of high scores) much easier. 

## Current status

* Menus aren't implemented, though the logic of the program's main loop should allow for them. You'd implement each menu and submenu as a `Context`.

* Core gameplay is implemented: all physics is implemented with *a priori* collision handling for the ball; the paddle is movable; blocks are breakable; difficulty thresholds work; and game logic exists to detect victory and loss conditions.

* The UI doesn't display the player's score, the number of tries, or what level the player is on.

* An input handler exists which captures keyboard and game controller input and allows it to be read in a "semantic" manner. Mouse input is not yet checked for or handled in any way. The input handler maps raw inputs, including by mapping them to "semantic inputs" (e.g. you don't have to check for Keyboard Esc and Gamepad Start; you can check for "Pause").

  * **Design flaw:** some inputs, like "pause" and "UI menu cancel," need to react only to buttons being pressed and then released. They currently only track whether the inputs in question are pressed down; they don't test whether the inputs in question are *newly* pressed down. This needs to be dealt with when handling raw inputs: we need to remember which raw inputs were previously down, and only react to a raw input (by marking the semantic input as active) if it's *newly* down.

* We render gameplay to an arbitrarily-sized playing field (its size computed based on the pixel sizes of our various graphics), and then downscale this to fit in the current window size. In other words, we've decoupled *logical sizes* within the game from *display sizes*, though the logical sizes aren't set in a terribly "logical" way. (The current logical size is 1844x2397: the width comes from the widths of the 14 blocks plus the widths of the gaps between them; and the height is the width * 1.3, which *very very roughly* matches the original Breakout.)

  * The above approach allows for varying sizes, but it does mean that graphics get downscaled pretty badly. **I'd like to investigate using the `cairo` package to do graphics-drawing at run-time.** Whenever the window size changes (or is initially set), the various gameplay elements could be rendered using graphics-drawing commands, with an effect akin to vector graphics. Gameplay could continue to use logical sizes, but graphics would be generated appropriately for display sizes and we could then blit directly to the output, without needing a downscale operation.

    * To clarify: the benefit of this is that we'd be able to use logical sizes that actually make sense, rather than weird stuff like 1844x2397 that feels hard to reason about. This, in turn, will make things like a settings file far more viable to work with.
  
  * We do take advantage of decoupling logical and display units: ball and paddle metrics (speed, width, etc.) are defined as percentages of the playing field's logical size. We'll probably want to do the same thing within the settings file, i.e. instead of saying "50 pixels" as a speed, say "0.2" i.e. 20% of the board's height as a speed. But if we choose better logical units (which will be easier if we can generate graphics programmatically) then maybe that won't be so important.

## Implementation notes

### Core program design and loop

The program is divided into multiple "contexts." Each context is a singleton subclass of the `Context` class, and represents a single "screen" that the player can "be on." For example, each menu and submenu is a separate context, and the core gameplay is also a context.

The `CONTEXT_MANAGER` singleton acts as a stack of "active contexts," with the "current context" being the one on the top of the stack (i.e. the one most recently added to the stack). The current context is able to process events and whatnot, while it and contexts beneath it can render to the screen. Think of it like layers in an image editor: you can only interact with the topmost layer, but you can see the layers beneath it, unless there's a fully opaque layer covering things up.

Contexts can also be thought of as reacting to the passage of time. The current context's `process` handler is given a "time delta" parameter which represents the amount of time that has passed since the last frame or game tick. This means that if you want some event to happen after a time delay, you'd want to track the passage of time within the context. (We provide a helper function, `Context._run_after`, which a context can use to schedule a function to run after a given delay in seconds.) This all also means that time passes independently within each context. If you start playing Breakout and then press the pause button, for example, then the pause menu will become the current context (because we open it by putting it on the top of the stack), and time will stop for the gameplay context (because it's now below something else on the stack).

The nice thing about this system is that it means that pausing the game happens basically for free: open any menu, and the gameplay context pauses because its processing is halted until it's no longer covered by another context. However, it does mean that covered-up contexts also can't do things like playing animations: even if they're visible, time has stopped for them. If we decide that this is an issue, we could perhaps make the time delta available to `Context.render`.

### Gameplay physics

The ball's movement uses *a priori* collision handling. We raycast forward from the ball's centerpoint, find the nearest collidable surface, and see if that surface is within range of the ball's speed (i.e. if the ball would hit the thing). If so, then we move the ball so that its edge lies at the collision point, and then adjust its velocity to bounce it away. Afterwards, we repeat the process, applying only the ball's remaining speed (i.e. the speed minus the distance by which the ball successfully traveled forward). We repeat this process until all of the ball's speed is consumed during the current game tick.

We originally attempted to use *a posteriori* collision handling, wherein we move the ball forward first and then check for intersections with other objects and resolve them. However, this led to occasional bugs where the ball could clip through blocks. In particular, if a fast-moving ball bounced into the corner of a "stalactite" i.e. an arrangement that looks like █▀ that, it could break the corner-joint block and then clip into that space and end up trapped. (Fortunately, the same problem would cause it to quickly clip out after frantically bouncing within its enclosure for a short time.) Anyway, issues like these were resolved with the switch to *a priori* collision handling, which, as a bonus, also turned out to be a bit cleaner to implement.

### Gamepad input

Gamepad input is currently handled by accessing Windows' XInput library directly. Unfortunately, this means that gamepad input is not supported on other platforms, nor with devices that aren't XInput-compatible (e.g. PlayStation 4 controllers without DS4Windows installed).

Input is handled this way because during testing, `pygame.joystick` was not correctly recognizing most inputs from a standard Xbox One controller (i.e. a standard XInput device, and one which works just fine with virtually every other game I have). Specifically, only the left and right triggers were being detected, and the number of buttons was also incorrect (sixteen: XInput *does* use a 16-bit value for button state, but two bits are unused). I was unable to debug this issue: `pygame.joystick` uses SDL under the hood; SDL supports *numerous* input devices, but based on a look at its source code, SDL prefers other Windows APIs over XInput whenever it thinks those APIs might work; and pygame doesn't expose any functions that would allow me to inspect what SDL is trying to do. It's all supposed to "just work," so it doesn't give you any tools to figure out what went wrong when it *doesn't* work.

Anyway, I (Dave) have experience using XInput in C++ programs, so I just wrote a Python wrapper for the XInput DLL using `ctypes`.