# readme.txt
# Kevin Christianson and Isaac Haseley, 3/12/16


1. A description of the program and its features:

    Our rendition of "Sorry!" is a 100% GUI version of the classic (4-piece, 4-color) board game. Hasbro's instructions are available online at http://www.hasbro.com/common/instruct/Sorry.PDF 
    The program supports up to four total players, and upon opening, the user selects the number of players and whether each is an AI or a real-world player. The game's turns are automatically simulated with the exception of real-world player decisions, so the user(s) need not draw cards. On-screen prompts and buttons guide the user experience.
    If you're new to "Sorry!" or haven't played in some time, we recommend beginning with a single AI and a single real-world player.
    For a complete user experience, turn on your volume before running the program.
    
    
2. A brief description/justification of how it is constructed:

    Objects: AI, Player(AI), Piece, Card, Deck, Status, and three different Buttons
    Players and AIs are each assigned four pieces of the appropriate color at the game's onset. The deck is shared among all players, and each turn, the active player begins by flipping a card, interpreting its value, and proceeding through a decision tree called "play_turn" that is unique to Player and AI. 
    For instance, if an AI draws a 3 (a boring number with no special text), it will check if there's a "Sorry!" move available (one which bumps an opposing piece back to Start), then check if there's a piece in front of its Start that it can relocate to make room for others to leave, then check if there's a move that will place a piece on a slide. At each check, the AI will take the corresponding action if it's available. If all checks fail, it will advance its furthest pawn 3 spaces. 
    In contrast, when the Player draws a 3, the program simply prompts them to select a piece to advance. 3 is an easy number to program the AI to move, however, cards like 11 or seven where there are many more options have more method calls for different situations trying to optimize the AI’s performance. 
    The Player is a subclass of AIPlayer, and so they share some methods and have similar inits. The methods they both use are ones that determine if moves are valid(try_move() and can_move()), translate piece locations based on player color(get_enemy_location(enemy)), and determine if pieces have been bumped or have slid(end_turn()). 
    As pieces move, the Piece class's draw method is hard at work determining where to display them in the graphics window. Each color defines their piece locations from 0 to 65 on the board (less than 0 is start and 65 is home). This means though that we sometimes have to translate one color’s piece to the correct location of another if that one wants to reference it, so we have functions like get_enemy_location(enemy) that are used by both player and AI and set_location() in the draw method in piece also takes in the color of the player who called it and so translates the piece’s location back into the piece’s correct location. 
    The different types of buttons are all similar and based on a Button class created in the textbook Python Programming by Zelle. One type of button is invisible onscreen and is used to accompany the pieces around the board. A second type of button is a visible one. The last type (ChoiceButton) is almost identical to the previous (it is a subclass of it) except that it must be activated for it to return its clicked method, while its superclass VisibleButton does not.
    Throughout the experience, methods in the Status class inform the user of unavailable and invalid moves and prompt the user to make decisions via on-screen text.
       
    
3. Instructions for running the program:

    To run the program, run final.py. 
    Line 1668 enables sounds. It's currently commented out because it has caused a crash when run on Windows 10. If you aren't using Windows 10, consider un-commenting line 1668. 