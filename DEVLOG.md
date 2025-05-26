
Not sure I'll remember to keep this updated, but just for my own sanity, this is a record of what parts of the program I got done, by day. Might help to keep my progress in perspective when I encounter setbacks.

&ndash; Dave

## Work done, by day:

### Day 1 (Thursday)
 - Core game behaviors
    - Paddle
    - Spawning blocks
    - *A posteriori* ball physics
    - Difficulty changes (paddle width, ball speed)
    - Scoring (though no UI)
 - General sketch for the main loop

Initial code was messy, but had promise. It was reassuring that I could get the most fundamental game behaviors done in just a day. I generally struggle with math, but I have a fair amount of experience doing lots of geometry-related code e.g. raycasts, and that experience definitely helped on Day 1.

### Day 2 (Friday)
 - Refactor and finalization of main loop structure (i.e. `Context` system created)
    - Refactor of core game behavior; significant code cleanup
 - Core game behaviors
    - Ball physics changed to *a priori*
    - Limited tries for the player (though no defeat handler yet &mdash; no menu to kick the player to)
    - Spawning a new ball if the player loses theirs
    - Levels and progression (though no victory handler yet &mdash; no menu to kick the player to)

Very satisfying. Like taking a heap of computer parts, all properly connected together but lying in a heap, and slotting them neatly into a case. This is the day the program really started coming together and taking its final shape.

### Day 3 (Saturday)
 - Text banners during play
    - UI prompt to serve the ball
    - UI messages for ball loss, game loss, level clear, game clear
 - XInput support

Less work than I'd planned... I was hoping to get started on the game menus, and had written down some ideas on how to structure some basic systems for them. Didn't get to that at all.

Still, though... It's not a bad amount of progress to make given the setbacks I hit. Pygame's joystick API completely failed to do its job, and researching how and why that happened took close to an hour and didn't lead to any fixes. I had to handwrite an XInput wrapper to do the library's job for it. Fortunately, I've had a few chances to use XInput natively before; that made writing the wrapper pretty easy even if it did take some time, so we can at least support most game controllers on Windows.

### Day 4 (Sunday)
 - HUD UI for showing the player's score, tries, and what level they're on
 - Now possible to tell if an input button was pressed on the current frame
 - Now possible to flag raw input buttons as "ignored"
    - We do this when contexts change, to prevent button presses from "bleeding through." For example, if you press B to back out of a submenu (bearing in mind that you'll likely have your thumb on the button for longer than a single frame), that same B-press shouldn't carry through to the parent menu and back you out of there, too. 
 - Wrote untested GUI helper types `Widget` and `Menu`
    - Code for activating UI widgets via mouse clicks or `INPUT_MANAGER.state.ui_activate` 
    - Code for keyboard navigation

Not as productive a day as I was hoping for; still haven't built the menus. I got stuck for a while trying to think of the best way to get the input manager to handle distinguishing key-down from key-hold, and implementing key auto-repeat. Figured out a solution for the former; the latter is non-essential and can wait.

Wrote some helper classes for GUI widgets and menus, sketching out keyboard navigation behavior. I'm basing this on systems I've studied and worked with before, but I'm going entirely from what I can recall offhand and what logically follows from that. Some aspects of the system are overkill, but it didn't take much effort to write those.

Anyway, tomorrow I can start putting these classes to use (and wiring up the rest of mouse input handling) and build some basic menus. They don't have to be pretty (that's what Week 6 of the course is for). Once I have the menus up and running, I can tackle the high-score storage. After that, a config file for game settings should be trivial-ish.

### Day 5 (Monday) 
TBD

### Day 6 (Tuesday)
TBD

Assignment due at day's end. Note that we also have to review *each other* (i.e. our appraisal of each other's contribution to the project) in a second assignment, and that's also due at day's end, so I will *not* have the full day to work on the code. Fortunately, though, this isn't a workday for me, so I might still have more time than on the previous few days.