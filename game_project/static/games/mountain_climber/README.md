# Mountain Climber

A simple platformer game where the goal is to stay alive. Falling off the bottom of the screen results in death and the level will restart. A level is completed by staying alive for long enough. For each level of the game, the speed at which the screen moves increases.

Run the game by opening `index.html` in any web browser.

Left and right arrow keys are used for moving. Up arrow key is used for jumping, letting go sooner results in a shorter jump.

The game supports full communication with the web service. Score is automatically submitted to the web service if dying or when finishing a level. Saving a game stores the current level along with the score at the start of the level. Loading that game state then restarts the same level.

