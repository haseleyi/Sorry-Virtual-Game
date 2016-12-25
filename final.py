# sorry.py
# Kevin Christianson and Isaac Haseley, 3/1/16

# import these to run game
import random
import time
from graphics import *

# import these to run sound
from subprocess import Popen
from multiprocessing import Process
from os import kill

class AIPlayer:
    def __init__(self, color, deck, window):
        self.color = color
        self.a = Piece(color, window, "a")
        self.b = Piece(color, window, "b")
        self.c = Piece(color, window, "c")
        self.d = Piece(color, window, "d")
        self.pieces = [self.a, self.b, self.c, self.d]
        self.start = 0
        self.home = 65
        self.at_start = True
        self.deck = deck
        # list of slide locations on the board
        self.slide_list = [13, 21, 28, 36, 43, 51]
        self.rivals = []
        self.window = window
        
    def get_color(self):
        return self.color

     # returns all the pieces for the player
    def return_pieces(self):
        return self.a, self.b, self.c, self.d

    # takes a list of all pieces in the game and removes the players own pieces so it has a list of enemy pieces
    def get_player_pieces(self, all_pieces):
        self.all_pieces = all_pieces[:]
        self.rivals = all_pieces[:]
        for piece in self.pieces:
            self.rivals.remove(piece)

    # moves piece as long as there isn't one of the player's own pieces in the way
    def try_move(self, target, amount):
        target_location = target.get_location()
        can_move = True
        for piece in self.pieces:
            piece_location = piece.get_location()
            if 65 > piece_location >= 0 and piece_location == target_location + amount:
                can_move = False
        if can_move:
            target.move(amount)
            return True
        return False

    # translate enemy location to player's reference
    def get_enemy_location(self, enemy):
        location = enemy.get_location()
        # if enemy is in safe zone, make sure they cannot be targeted
        if location > 59:
            return -1
        if location < 0:
            return -1
        # based on this player's color, adjust enemy piece location to this player's system
        if self.color == "Blue":
            color = enemy.get_color()
            if color == "Red":
                return (location - 15) % 60
            elif color == "Yellow":
                return (location + 15) % 60
            elif color == "Green":
                return (location + 30) % 60
        elif self.color == "Red":
            color = enemy.get_color()
            if color == "Blue":
                return (location + 15) % 60
            elif color == "Yellow":
                return (location + 30) % 60
            elif color == "Green":
                return (location - 15) % 60
        elif self.color == "Yellow":
            color = enemy.get_color()
            if color == "Red":
                return (location + 30) % 60
            elif color == "Blue":
                return (location - 15) % 60
            elif color == "Green":
                return (location + 15) % 60
        elif self.color == "Green":
            color = enemy.get_color()
            if color == "Red":
                return (location + 15) % 60
            elif color == "Yellow":
                return (location - 15) % 60
            elif color == "Blue":
                return (location + 30) % 60
        return location

    # see if the player has viable moves with the given card (returns True or False)
    def can_move(self, value):
        # set card 4 value to its move value of backwards 4
        if value == 4:
            value = -4
        # special case for sorry card, see if you have a piece in Start and an enemy out of Start 
        elif value == "Sorry!":
            self.at_start = False
            for piece in self.pieces:
                if piece.get_location() < 0:
                    self.at_start = True
                    break
            if self.at_start:
                for enemy in self.rivals:
                    if self.get_enemy_location(enemy) >= 0:
                        return True
            return False
        # special case for seven because it can be distributed among pieces
        elif value == 7:
            for piece in self.pieces:
                piece_location = piece.get_location()
                if piece_location >= 0:
                    value -= (65 - piece_location)
            if value <= 0:
                return True
            return False
        # if there is a piece out of start that can move with the given 
            # value without hitting another one of the player's pieces, returns True
        for piece in self.pieces:
            piece_location = piece.get_location()
            if piece_location >= 0:
                if piece_location + value <= 65:
                    for piece2 in self.pieces:
                        if 0 <= piece2.get_location() <65 and piece2 != piece:
                            if (piece2.get_location() != piece_location + value):
                                return True
                    move = 0
                    for piece2 in self.pieces:
                        if piece2.get_location() < 0 or piece2.get_location() == 65:
                            move += 1
                    if move == 3:
                        return True
        if value == 10:
            return self.can_move(-1)
        return False

    # sees if the AI has a piece at location 1, directly outside of Start
    # (AI wants to move it so more pieces can come out of start)
    def piece_blocking_start(self, number):
        if self.at_start:
            for piece in self.pieces:
                piece_location = piece.get_location()
                if piece_location == 1:
                    go = True
                    if piece_location + number in self.slide_list:
                        # check to make sure moving that number wouldn't Sorry! a friendly piece
                        for piece2 in self.pieces:
                            if piece2 != piece and (piece2.get_location() - (piece_location + number)) < 5:
                                go = False
                    if go and self.try_move(piece, number):
                        return True
        return False
     
    # finds whichever piece is the furthest along and moves it by given amount
    def move_furthest_along(self, amount):
        distance = -1
        for piece in self.pieces:
            location = piece.get_location()
            if location > distance:
                if location + amount <= 65:
                    distance = location
                    pointer = piece
        try:
            self.try_move(pointer, amount)
            return True
        except:
            return False
    
    # sees if any of the pieces can Sorry! an enemy piece 
    def sorry_move(self, amount):
        for piece in self.pieces:
            piece_location = piece.get_location()
            if 65 > piece_location > 0:  
                for enemy in self.rivals:
                    distance = self.get_enemy_location(enemy)
                    if distance >= 0:
                        if  piece.get_location() + amount == distance:
                            piece.move(amount)
                            enemy.go_start()
                            return True
        return False
    
    # sees if any of the pieces can land on a slide
    def slide(self, amount):    
        for piece in self.pieces:
            piece_location = piece.get_location()
            if piece_location + amount in self.slide_list:
                move = True
                # check to make sure sliding won't Sorry! another of the AI's pieces
                for piece2 in self.pieces:
                    if piece2 != piece:
                        if piece2.get_location() - (piece_location + amount) < 5:
                            move = False
                if move:
                    piece.move(amount)
                    return True
        return False
    
    # move the AI's piece with the smallest value
    def move_last(self, amount):
        # moves the last piece
        distance = 65
        for piece in self.pieces:
            compare_distance = piece.get_location()
            if 0 <= compare_distance < distance:
                if compare_distance + amount <= 65:
                    distance = compare_distance
                    pointer = piece
        try:
            if self.try_move(pointer, amount):
                return True
            return False
        except:
            return False

    # for standard values, finds the most optimal move
    def boring_number(self, number):
        if self.sorry_move(number):
            return True
        if self.piece_blocking_start(number):
            return True
        if self.slide(number):
            return True
        if self.move_furthest_along(number):
            return True
        return False
            
    # only called if the player has pieces in start. Moves the piece the given distance out of start
    def one_or_two(self, number):
        if self.a.get_location() < 0:
            self.a.set_location(number, self.color)
            return
        if self.b.get_location() < 0:
            self.b.set_location(number, self.color)
            return
        if self.c.get_location() < 0:
            self.c.set_location(number, self.color)
            return
        else:
            self.d.set_location(number, self.color)
        
    # finds the optimal move for a card value of 4 (move backwards 4)
    def four(self):
        # sees if the piece is close enough to start so that going backwards would be advantageous
        for piece in self.pieces:
            if 0 <= piece.get_location() < 4:
                if self.try_move(piece, -4):
                    return
        if self.sorry_move(-4):
            return
        if self.slide(-4):
            return
        if self.move_last(-4):
            return
        return
    
    # sees if any of the pieces can Sorry! an enemy piece and loops until no more can
    def seven_sorry(self, distance_left):
        for piece in self.pieces:
            for enemy in self.rivals:
                distance = self.get_enemy_location(enemy)
                if distance >= 0:
                    distance -= piece.get_location()
                    if 0 < distance <= distance_left:
                        piece.move(distance)
                        distance_left -= distance
        return distance_left

    # sees if any of the pieces can slide and loops until no more can
    def seven_slide(self, amount):
        for piece in self.pieces:
            for location in self.slide_list:
                distance = location - piece.get_location()
                if 0 < distance <= amount:
                    if self.try_move(piece, distance):
                        amount -= distance
        return amount
    
    # sees if any of the pieces can move home and loops until no more can
    def seven_move_home(self, amount):
        for piece in self.pieces:
            amount_needed = self.home - piece.get_location()
            if 0 < amount_needed <= amount:
                if self.try_move(piece, amount_needed):
                    amount -= amount_needed
                    if amount > 0:
                        return self.seven_move_home(amount)
                    return amount
        return amount
    
    # finds the optimal moves for a seven card (can split up value among all pieces)
    def seven(self):
        distance_left = self.seven_sorry(7)
        if distance_left > 0:
            distance_left = self.seven_move_home(distance_left)
        if distance_left > 0:
            if self.piece_blocking_start(distance_left):
                return
        if distance_left > 0:
            distance_left = self.seven_slide(distance_left)
        if distance_left > 0:
            self.move_furthest_along(distance_left)
        
    # finds the most optimal move for a value of ten (forward 10 or backwards 1)
    def ten(self):
        for piece in self.pieces:
            if piece.get_location() == 0:
                if self.try_move(piece, -1):
                    return
        if self.sorry_move(10):
            return
        if self.sorry_move(-1):
            return
        if self.piece_blocking_start(-1):
            return
        if self.slide(10):
            return
        if self.move_furthest_along(10):
            return
        if self.slide(-1):
            return
        self.move_last(-1)

    # sees if AI can switch pieces with an enemy, then sees if it is advantageous to do so
    def eleven(self):
        #checks to see if moving a piece forward 11 is a valid choice
        normal = False
        if self.can_move(11):
            normal = True
            if self.sorry_move(11):
                return
        # get our last piece
        distance = 60
        for piece in self.pieces:
            compare_distance = piece.get_location()
            if 0 <= compare_distance < distance:
                distance = compare_distance
                pointer = piece
                pointer_location = compare_distance
        try:
            pointer.get_location()
        except:
            if normal:
                self.boring_number(11)
            else:
                status_bar.ai_no_moves(self.color)
            return
        # get the enemy piece closest to our home
        target_location = -1
        for enemy in self.rivals:
            location = self.get_enemy_location(enemy)
            if location > target_location:
                target = enemy
                target_location = location
        try:
            target.get_location()
        except:
            if normal:
                self.boring_number(11)
            else:
                status_bar.ai_no_moves(self.color)
            return
        # sees if an enemy piece is closer to scoring that we 
            # would be if we swapped with the piece closest to our home
        # if so, switch with enemy piece, otherwise switch with the piece closest to our home
        new_target, new_target_location = self.prevent_enemy()
        if new_target != 0:
            # check to see if swapping with the enemy piece closest to their home is 
                # more advantageous than swapping with the enemy piece closest to our home
            # see if they are closer to their home than they are to mine. Also, they must be 
                # ahead of us or we must be past their start for it to be a good move
            if new_target_location > target_location and (self.get_enemy_location(new_target) >
                    pointer_location or pointer_location > 15 + self.get_enemy_location(new_target)):
                pointer.set_location(self.get_enemy_location(new_target), self.color)
                new_target.set_location(pointer_location, self.color)
                return
            elif target_location - pointer_location > 5:
                target.set_location(pointer_location, self.color)
                pointer.set_location(target_location, self.color)
                return
            elif normal:
                self.boring_number(11)
                return
        if not normal:
            # if it is more advantageous to swap pieces rather than move forward 11, do so
            if target_location - pointer_location > 5:
                target.set_location(pointer_location, self.color)
                pointer.set_location(target_location, self.color)
                return
            else:
                status_bar.ai_choose_no_moves(self.color)
        else:
            if target_location - pointer_location > 5:
                target.set_location(pointer_location, self.color)
                pointer.set_location(target_location, self.color)
                return
            else:
                # otherwise, move normally
                self.boring_number(11)

    # if an enemy is close to scoring, returns the enemy and its location
    def prevent_enemy(self):
        distance = 45
        for enemy in self.rivals:
            enemy_location = enemy.get_location()
            if 60 > enemy_location > distance:
                distance = enemy_location
                target = enemy
        try:
            return target, distance
        except:
            return 0,0

    # finds the most advantageous piece to Sorry! if able
    def sorry(self):
        # gets the furthest enemy
        distance = -1
        for enemy in self.rivals:
            enemy_location = self.get_enemy_location(enemy)
            if enemy_location > distance:
                distance = enemy_location
                target = enemy
        # sees if an enemy is close to scoring. If so, Sorry! them, otherwise Sorry! furthest enemy
        new_target, new_target_location = self.prevent_enemy()
        if new_target != 0:
            if new_target_location > distance:
                try:
                    for piece in self.pieces:
                        if piece.get_location() < 0:
                            piece.set_location(self.get_enemy_location(new_target), self.color)
                            new_target.go_start()
                            return True
                except:
                    return False
            else:
                 try:
                    target.go_start()
                    for piece in self.pieces:
                        if piece.get_location() < 0:
                            piece.set_location(distance, self.color)
                            return True
                 except:
                    return False
        try:
            target.go_start()
            for piece in self.pieces:
                if piece.get_location() < 0:
                    piece.set_location(distance, self.color)
                    return True
        except:
            return False
        return False
        
    # plays the AI turn: draws a card and depending on value, calls appropriate function(s)
    def play_turn(self):
        status_bar.undraw()
        deck.ai_flip()
        time.sleep(1)
        value = deck.get_card()
        # possible to move a piece out of start
        if value == 1 or value == 2:
            # see if there is a piece in start
            self.at_start = False
            for piece in self.pieces:
                piece_location = piece.get_location()
                if piece_location < 0:
                    self.at_start = True
                    break
            # see if there is a piece preventing moving a piece from start
            for piece in self.pieces:
                    if piece.get_location() == 1:
                        if self.can_move(value):
                            self.boring_number(value)
                            self.end_turn()
                            if value == 2:
                                status_bar.extra_turn()
                                self.play_turn()
                            return self.end_turn()
            # if can move a piece from start, do so
            if self.at_start:
                self.one_or_two(1)
            # otherwise, if can move a piece that distance, do so
            elif self.can_move(value):
                self.boring_number(value)
            # if the card is a two, draw again
            if value == 2:
                self.end_turn()
                status_bar.extra_turn()
                self.play_turn()
            return self.end_turn()
        elif self.can_move(value):
            if value == 4:
                self.four()
            elif value == 7:
                self.seven()
            elif value == 10:
                self.ten()
            elif value == "Sorry!":
                self.sorry()
            elif value != 11:
                self.boring_number(value)
        elif value != 11:
            status_bar.undraw_2()
            status_bar.ai_no_moves(self.color)
        if value == 11:
            self.eleven()
            return self.end_turn()
        return self.end_turn()

    # checks for slides and Sorry!s and moves the pieces accordingly. Also adjusts player's score
    def end_turn(self):
        status_bar.undraw()
        score = 0
        for piece in self.all_pieces:
            piece_location = piece.get_location()
            if piece_location >= 0:
                # if the piece is on a slide
                if piece_location in self.slide_list:
                    time.sleep(1)
                    status_bar.slide()
                    # check if it's a three or four length slide
                    if self.slide_list.index(piece_location) % 2:
                        # can Sorry! any piece along a slide (yours included)
                        for enemy in self.all_pieces:
                            distance = self.get_enemy_location(enemy) - piece_location
                            if 0 < distance <= 4:
                                enemy.go_start()
                        piece.move(4)
                    else:
                        # can Sorry! any piece along a slide (yours included)
                        for enemy in self.all_pieces:
                            distance = self.get_enemy_location(enemy) - piece_location
                            if 0 < distance <= 3:
                                enemy.go_start()
                        piece.move(3)
                if piece.get_color() == self.color:
                    # for every piece in your home, add to your score
                    if piece_location == 65:
                        score += 1
                    # if your piece is on the same square as an enemy, send them home
                    for enemy in self.rivals:
                        if self.get_enemy_location(enemy) == piece_location:
                            enemy.go_start()
        status_bar.undraw()
        # check to see if the game is over
        if score == 4:
            return True
        return False
            

class Player(AIPlayer):
        def __init__(self, color, deck, window, yes, no):
            # same init as AI, but have yes and no buttons for deciding choices
            super().__init__(color, deck, window)
            self.yes_button = yes
            self.no_button = no

        # for all normal card values or if player decided to play card as normal
        def normal_move(self, value):
            # prompt user to pick one of his/her pieces
            status_bar.click(self.color)
            while True:
                choice = self.window.getMouse()
                for piece in self.pieces:
                    if piece.was_clicked(choice):
                        piece_location = piece.get_location()
                        if piece_location >= 0:
                            if piece_location + value > 65:
                                # prompt them again if the piece is invalid
                                status_bar.not_valid()
                                self.normal_move(value)
                                return
                            else:
                                if self.try_move(piece, value):
                                    return
                                else:
                                    status_bar.not_valid()
                                    self.normal_move(value)
                                    return
                        else:
                            status_bar.not_valid()
                            self.normal_move(value)
                            return
                        
        # called if player has at least one piece at their start
        # allows them to select piece to move out of start
        def one_or_two(self, value):
            status_bar.click(self.color)
            choice = self.window.getMouse()
            for piece in self.pieces:
                if piece.was_clicked(choice):
                    if piece.get_location() >= 0:
                        self.one_or_two(value)
                    else:
                        piece.set_location(value, self.color)
                        return
            self.one_or_two(value)

        # prompts the player to pick which piece to move backwards four
        def four(self):
            status_bar.click(self.color)
            while True:
                choice = self.window.getMouse()
                for piece in self.pieces:
                    if piece.was_clicked(choice):
                        if 65 > piece.get_location() >= 0:
                            if self.try_move(piece, -4):
                                return
                            else:
                                status_bar.not_valid()
                                self.four()
                                return
                        else:
                            status_bar.not_valid()
                            self.four()
                            
        # recursive function that allows the player to move seven times, one piece one spot at a time
        # takes a list and stores all the moves in that list
        def seven(self, number, move_list):
            status_bar.seven(number, self.color)
            choice = self.window.getMouse()
            for piece in self.pieces:
                if piece.was_clicked(choice):
                    piece_location = piece.get_location()
                    if piece_location >= 0:
                        if 1 <= number:
                            if piece_location + 1 <= 65:
                                self.seven_move_list(move_list, piece)
                                piece.move(1)
                                number -= 1
                                if number > 0:
                                    self.seven(number, move_list)
                                return self.seven_end(move_list)
                            else:
                                status_bar.not_valid()
                                self.seven(number, move_list)
                                return
                        else:
                            status_bar.not_valid()
                            self.seven(number, move_list)
                            return
                    else:
                        status_bar.not_valid()
                        self.seven(number, move_list)
                        return
            self.seven(number, move_list)

        # every time a piece is moved, add that piece to the move_list
        def seven_move_list(self, move_list, piece):
            move_list.append(piece)

        # checks to see that all moves were valid 
        # if they were not, moves all pieces back and starts seven over
        def seven_end(self, move_list):
            for piece in self.pieces:
                for piece2 in self.pieces:
                    if piece2 != piece:
                        # if two of the same color pieces are in the same position, reset
                        if piece2.get_location() == piece.get_location() and piece.get_location() != 65:
                            status_bar.not_valid()
                            # unmove all pieces and start over
                            for item in move_list:
                                item.move(-1)
                            move_list = []
                            return self.seven(7, move_list)

        # prompts the user to decide which piece to move and if they want to move it forward 10 or backwards 1
        def ten(self):
            status_bar.click(self.color)
            choice = self.window.getMouse()
            for piece in self.pieces:
                if piece.was_clicked(choice):
                    piece_location = piece.get_location()
                    # checks to make sure it was a valid piece to select
                    if 65 > piece_location >= 0:
                        # ask if they want to move piece forwards or backwards
                        status_bar.ten(self.color)
                        self.yes_button.activate()
                        self.no_button.activate()
                        while True:
                            choice = self.window.getMouse()
                            if self.yes_button.clicked(choice):
                                self.yes_button.deactivate()
                                self.no_button.deactivate()
                                if self.try_move(piece, -1):
                                    return
                                else:
                                    status_bar.not_valid()
                                    self.ten()
                                    return
                            elif self.no_button.clicked(choice):
                                self.yes_button.deactivate()
                                self.no_button.deactivate()
                                if piece_location + 10 <= 65:
                                    if self.try_move(piece, 10):
                                        return
                                    else:
                                        status_bar.not_valid()
                                        self.ten()
                                        return
                                else:
                                    status_bar.not_valid()
                                    self.ten()
                                    return
                    else:
                        status_bar.not_valid()
                        self.ten()
                        return
            self.ten()
            
        # called if the player wants to swap pieces
        def eleven_swap(self):
            # get the selected enemy
            status_bar.eleven_swap(1, self.color)
            switch= True
            while switch:
                target = self.window.getMouse()
                for enemy in self.rivals:
                    if enemy.was_clicked(target):
                        # make sure the enemy is a valid target
                        if 60 > enemy.get_location() >= 0:
                            switch = False
                            break
            # check to make sure enemy was selected correctly
            try:
                enemy.get_location()
            except:
                return self.eleven_swap()
            # get the player's piece to swap
            status_bar.eleven_swap(2, self.color)
            switch = True
            while switch:
                choice = self.window.getMouse()
                for piece in self.pieces:
                    if piece.was_clicked(choice):
                        piece_location = piece.get_location()
                        if 59 > piece_location > 0:
                            switch = False
                            break
            # swap the pieces if valid, otherwise start over
            try:
                piece.set_location(self.get_enemy_location(enemy), self.color)
                enemy.set_location(piece_location, self.color)
            except:
                self.eleven_swap()
                
        # has the player click on a valid enemy and that enemy will be sent to start 
        # a player's piece in start will be set to that location
        # only called if player has pieces in start
        def sorry(self):
            # get the player's choice of enemy to sorry
            choice = self.window.getMouse()
            for enemy in self.rivals:
                if enemy.was_clicked(choice):
                    enemy_location = self.get_enemy_location(enemy)
                    # make sure it's a valid selection
                    if enemy_location >= 0:
                        # get the first piece in start
                        for piece in self.pieces:
                            if piece.get_location() < 0:
                                break
                        piece.set_location(enemy_location, self.color)
                        enemy.go_start()
                        return
                    else:
                        status_bar.not_valid()
                        self.sorry()
                        return
            status_bar.not_valid()
            self.sorry()

        def play_turn(self):
            status_bar.undraw()
            deck.flip()
            value = deck.get_card()
            if value == 1 or value == 2:
                # see if there is a piece in start
                self.at_start = False
                for piece in self.pieces:
                    piece_location = piece.get_location()
                    if piece_location < 0:
                        self.at_start = True
                        break
                # see if there is a piece preventing moving a piece from start
                for piece in self.pieces:
                        if piece.get_location() == 1:
                            status_bar.no_at_start(self.color)
                            if self.can_move(value):
                                self.normal_move(value)
                                if value == 2:
                                    self.end_turn()
                                    status_bar.extra_turn()
                                    self.play_turn()
                            return self.end_turn()
                # if the player can move from start and move normally, prompts them to decide which to do
                if self.at_start and self.can_move(value):
                    status_bar.start_move(self.color)
                    self.yes_button.activate()
                    self.no_button.activate()
                    decided = False
                    while not decided:
                        choice = self.window.getMouse()
                        if self.yes_button.clicked(choice):
                            self.yes_button.deactivate()
                            self.no_button.deactivate()
                            self.one_or_two(1)
                            # draw again if card is a two
                            if value == 2:
                                self.end_turn()
                                status_bar.extra_turn()
                                self.play_turn()
                            return self.end_turn()
                        elif self.no_button.clicked(choice):
                            self.yes_button.deactivate()
                            self.no_button.deactivate()
                            decided = True
                # if they can only move a piece from start, run that method
                elif self.at_start:
                    self.one_or_two(1)
                    # draw again if card is a two
                    if value == 2:
                        self.end_turn()
                        status_bar.extra_turn()
                        self.play_turn()
                    return self.end_turn()
                # if cannot move from start, then move normally
                if self.can_move(value):
                    self.normal_move(value)
                else:
                    status_bar.no_moves(self.color)
                # if card is two draw again
                if value == 2:
                    self.end_turn()
                    status_bar.extra_turn()
                    self.play_turn()
                return self.end_turn()
            # check to see if the player can move with the given value
            # if so, then calls the appropriate method
            elif self.can_move(value):
                if value == 4:
                    self.four()
                elif value == 7:
                    move_list = []
                    self.seven(7, move_list)
                elif value == 10:
                    self.ten()
                elif value == 11:
                    # check if player has a piece out of start
                    can_switch = False
                    for piece in self.pieces:
                        if 0 <= piece.get_location() < 60:
                            can_switch = True
                    # if so, see if the enemy has a piece out of start
                    if can_switch:
                        can_switch = False
                        for enemy in self.rivals:
                            if self.get_enemy_location(enemy) >= 0:
                                can_switch = True
                                break
                        # if both are true, prompt player to decide if they want to move normally or switch
                        if can_switch:
                            status_bar.eleven_1(self.color)
                            self.yes_button.activate()
                            self.no_button.activate()
                            decided = False
                            while not decided:
                                choice = self.window.getMouse()
                                if self.yes_button.clicked(choice):
                                    self.yes_button.deactivate()
                                    self.no_button.deactivate()
                                    self.eleven_swap()
                                    decided = True
                                elif self.no_button.clicked(choice):
                                    self.yes_button.deactivate()
                                    self.no_button.deactivate()
                                    self.normal_move(value)
                                    decided = True
                        else:
                            self.normal_move(value)
                    else:
                        self.normal_move(value)
                elif value == "Sorry!":
                    status_bar.sorry_banner_2(self.color)
                    self.sorry()
                else:
                    self.normal_move(value)
            elif value == 11:
                # even if player cannot move 11 forward, check to see if they could switch with an enemy player's piece
                me = False
                for piece in self.pieces:
                    if 59 >= piece.get_location() >= 0:
                        me = True
                        break
                them = False
                for enemy in self.rivals:
                    if self.get_enemy_location(enemy) >= 0:
                        them = True
                        break
                # if so, give them the option to switch or not move
                if me and them:
                    self.yes_button.activate()
                    self.no_button.activate()
                    decided = False
                    while not decided:
                        choice = self.window.getMouse()
                        if self.yes_button.clicked(choice):
                            self.yes_button.deactivate()
                            self.no_button.deactivate()
                            self.eleven_swap()
                            decided = True
                        elif self.no_button.clicked(choice):
                            self.yes_button.deactivate()
                            self.no_button.deactivate()
                            decided = True
                else:
                    status_bar.no_moves(self.color)
            else:
                status_bar.no_moves(self.color)
                
            return self.end_turn()

        
class Piece:

    def __init__(self, color, window, name):
        self.color = color
        self.name = name
        if color == "Green":
            self.image = "green_piece.gif"
        if color == "Red":
            self.image = "red_piece.gif"
        if color == "Blue":
            self.image = "blue_piece.gif"
        if color == "Yellow":
            self.image = "yellow_piece.gif"
        self.location = self.get_start_location()
        self.on_screen = Image(start_location_dictionary[self.location], self.image)
        self.button = Button(window, self.display_location(), 40, 50, self.name)
        self.draw()

    # returns true if the piece's button was clicked on
    def was_clicked(self, mouse):
        if self.button.clicked(mouse):
            return True
        return False

    # gets the piece's location when it's in start
    def get_start_location(self):
        if self.color == "Green":
            loc_dict = {"a": -1, "b": -2, "c": -3, "d": -4}
            return loc_dict[self.name]
        elif self.color == "Red":
            loc_dict = {"a": -5, "b": -6, "c": -7, "d": -8}
            return loc_dict[self.name]
        elif self.color == "Blue":
            loc_dict = {"a": -9, "b": -10, "c": -11, "d": -12}
            return loc_dict[self.name]
        elif self.color == "Yellow":
            loc_dict = {"a": -13, "b": -14, "c": -15, "d": -16}
            return loc_dict[self.name]

    def get_color(self):
        return self.color

    def get_location(self):
        return self.location

    # moves the piece the given distance and draws it
    def move(self, distance):
        self.location = self.location + distance
        # if the piece moved backwards from start, set it to being toward the end
        if self.location < 0:
            self.location = self.location % 60
        self.draw()

    # sets the piece's location to the location given, adjusted by the color of the player that sets it
    def set_location(self, location, color):
        if self.color == "Blue":
            if color == "Red":
                self.location = (location - 15) % 60
            elif color == "Yellow":
                self.location = (location + 15) % 60
            elif color == "Green":
                self.location = (location + 30) % 60
            else:
                self.location = location
        elif self.color == "Red":
            if color == "Blue":
                self.location = (location + 15) % 60
            elif color == "Yellow":
                self.location = (location + 30) % 60
            elif color == "Green":
                self.location = (location - 16) % 60
            else:
                self.location = location
        elif self.color == "Yellow":
            if color == "Red":
                self.location = (location + 30) % 60
            elif color == "Blue":
                self.location = (location - 15) % 60
            elif color == "Green":
                self.location = (location + 15) % 60
            else:
                self.location = location
        elif self.color == "Green":
            if color == "Red":
                self.location = (location + 15) % 60
            elif color == "Yellow":
                self.location = (location - 15) % 60
            elif color == "Blue":
                self.location = (location + 30) % 60
            else:
                self.location = location
        self.draw()

    # set a piece back to start
    def go_start(self):
        self.location = self.get_start_location()
        self.draw()

    # displays the piece on the board
    def draw(self):
        self.undraw()
        # checks if piece is at start
        if self.location < 0:
            self.on_screen = Image(start_location_dictionary[self.location], self.image)
        # checks if piece is at home
        elif self.location == 65:
            if self.color == "Green":
                self.on_screen = Image(green_home_location_dictionary[self.name], self.image)
            elif self.color == "Blue":
                self.on_screen = Image(blue_home_location_dictionary[self.name], self.image)
            elif self.color == "Red":
                self.on_screen = Image(red_home_location_dictionary[self.name], self.image)
            elif self.color == "Yellow":
                self.on_screen = Image(yellow_home_location_dictionary[self.name], self.image)
        # checks if piece is in a safe zone
        elif 59 < self.location < 65:
            if self.color == "Green":
                self.on_screen = Image(green_safe_location_dictionary[self.location], self.image)
            elif self.color == "Blue":
                self.on_screen = Image(blue_safe_location_dictionary[self.location], self.image)
            elif self.color == "Red":
                self.on_screen = Image(red_safe_location_dictionary[self.location], self.image)
            elif self.color == "Yellow":
                self.on_screen = Image(yellow_safe_location_dictionary[self.location], self.image)
        # if none of the above, piece is on a border space
        else:
            # adjust piece location to yellow location
            loc = self.location
            if self.color == "Red":
                loc = (loc + 30) % 60
            elif self.color == "Blue":
                loc = (loc - 15) % 60
            elif self.color == "Green":
                loc = (loc + 15) % 60
            if 0 <= loc <= 12:
                self.on_screen = Image(Point(170 + 44 * loc, 40), self.image)
            elif 13 <= loc <= 27:
                self.on_screen = Image(Point(698, 84.5 + 44.5 * (loc - 13)), self.image)
            elif 28 <= loc <= 42:
                self.on_screen = Image(Point(698 - 44 * (loc - 27), 707.5), self.image)
            elif 43 <= loc <= 57:
                self.on_screen = Image(Point(37, 707.5 - 44.5 * (loc - 42)), self.image)
            elif loc == 58:
                self.on_screen = Image(Point(82, 40), self.image)
            elif loc == 59:
                self.on_screen = Image(Point(126, 40), self.image)
        self.on_screen.draw(win)
        self.button.set_location(self.display_location())
        self.button.activate()

    # returns piece's coordinate location
    def display_location(self):
        return self.on_screen.getAnchor()

    # remove piece from screen
    def undraw(self):
        self.on_screen.undraw()

        
class Deck:

    def __init__(self):
        self.cards = [Card(1)] * 5 + [Card("Sorry!"), Card(2), Card(3),
            Card(4), Card(5),Card(7), Card(8), Card(10), Card(11), Card(12)] * 4
        self.discard = []

    def shuffle(self):
        random.shuffle(self.cards)

    # gets next card, called by AI
    def ai_flip(self):
        if len(self.cards) > 0:
            status_bar.draw()
            self.discard.append(self.cards[0])
            del self.cards[0]
        else:
            self.re_shuffle()
            status_bar.draw()
            self.discard.append(self.cards[0])
            del self.cards[0]

    # gets next card, called by Player (this flip displays a message)
    def flip(self):
        if len(self.cards) > 0:
            status_bar.draw()
            status_bar.draw_message()
            self.discard.append(self.cards[0])
            del self.cards[0]
        else:
            self.re_shuffle()
            status_bar.draw()
            status_bar.draw_message()
            self.discard.append(self.cards[0])
            del self.cards[0]

    # returns the card value of the last flipped card
    def get_card(self):
        return self.discard[-1].get_value()

    # put discarded cards back into deck and shuffle them
    def re_shuffle(self):
        self.cards = self.discard[:]
        self.discard = []
        self.shuffle()


class Card:

    def __init__(self, value):
        self.value = value
        self.message = self.get_message()

    # returns the message of the card based on the card's value
    def get_message(self):
        message_dict = {1: "Move from Start OR move 1.", 2: 
            "Move 1 from Start OR move 2. Go again.", 3: 
            "Move 3.", 4: "Move 4 backward.", 5: "Move 5.", 
            7: "Make 7 selections. Each moves 1 space.", 8: "Move 8.", 10: 
            "Move 10 forward OR 1 backward.", 
            11: "Move 11 OR switch places with an opposing pawn.", 
            12: "Move 12.", "Sorry!": "Select a pawn to ruin its day."}
        return message_dict[self.value]

    def get_value(self):
        return self.value

    # displays card value and message
    def draw(self):
        status_bar.draw()
        
        
class Button:
    # a button is a labeled rectangle in a window
    # it is activated or deactivated with the activate() and deactivate() methods
    # the clicked(p) method returns true if the button is active and p is inside it

    # * * * these buttons are not visible and are used on the pieces

    def __init__(self, win, center, width, height, label):
        # creates a rectangular button
        # ex: qp = Button(myWin, centerPoint, width, height, 'Exit Game')
        self.width = width/2.0
        self.height = height/2.0
        w,h = width/2.0, height/2.0
        x,y = center.getX(), center.getY()
        self.xmax, self.xmin = x+w, x-w
        self.ymax, self.ymin = y+h, y-h
        self.deactivate()

    def set_location(self, center):
        x,y = center.getX(), center.getY()
        self.xmax, self.xmin = x+self.width, x-self.width
        self.ymax, self.ymin = y+self.height, y-self.height

    def clicked(self, p):
        # returns true if button is active and p is inside
        return (self.active and self.xmin <= p.getX() <= self.xmax and self.ymin <= p.getY() <= self.ymax)

    def get_label(selfself):
        # returns the label string of this button
        return self.label.getText()

    def activate(self):
        # sets button to 'active'
        self.active = True

    def deactivate(self):
        # sets button to 'inactive'
        self.active = False


class VisibleButton():
    def __init__(self, win, center, width, height, label, color):
        # creates a rectangular button
        # ex: qp = Button(myWin, centerPoint, width, height, 'Exit Game')
        self.color = color
        self.width = width/2.0
        self.height = height/2.0
        w,h = width/2.0, height/2.0
        x,y = center.getX(), center.getY()
        self.xmax, self.xmin = x+w, x-w
        self.ymax, self.ymin = y+h, y-h
        p1 = Point(self.xmin, self.ymin)
        p2 = Point(self.xmax, self.ymax)
        self.rect = Rectangle(p1,p2)
        self.rect.setFill('lightgray')
        self.rect.setOutline('lightgray')
        self.rect.draw(win)
        self.label = Text(center, label)
        self.label.draw(win)
        self.deactivate()

    def set_location(self, center):
        x,y = center.getX(), center.getY()
        self.xmax, self.xmin = x+self.width, x-self.width
        self.ymax, self.ymin = y+self.height, y-self.height
        p1 = Point(self.xmin, self.ymin)
        p2 = Point(self.xmax, self.ymax)
        self.rect = Rectangle(p1,p2)

    def clicked(self, p):
        # returns true if button is active and p is inside
        return (self.xmin <= p.getX() <= self.xmax and self.ymin <= p.getY() <= self.ymax)

    def get_label(self):
        # returns the label string of this button
        return self.label.getText()

    def get_color(self):
        return self.color

    def status(self):
        return self.active

    def activate(self):
        # sets button to 'active'
        self.label.setFill('black')
        self.rect.setWidth(2)
        self.active = True

    def deactivate(self):
        # sets button to 'inactive'
        self.label.setFill('darkgrey')
        self.rect.setWidth(1)
        self.active = False

    def __enter__(self):
        self.label.setFill('black')
        self.rect.setWidth(2)
        self.active = True
        return self

    def __exit__(self, one, two, three):
        pass
    
    def set_label_size(self, number):
        self.label.setSize(number)

        
class ChoiceButton(VisibleButton):
    # the only difference between this button and VisibleButton is that 
    # this button will only return clicked if it has been activated
        def clicked(self, p):
            # returns true if button is active and p is inside
            return (self.active and self.xmin <= p.getX() <= self.xmax and self.ymin <= p.getY() <= self.ymax)

        
class Status:
    
    # displays welcome message
    # uses a top banner and a bottom banner
    def __init__(self):
        self.final_banner = Text(Point(375, 215), "Welcome to \"SORRY!\"")
        self.style(1, 24, "bold", "white")
        self.final_banner_2 = Text(Point(368, 535), "Turn on sound!")
        self.style(2, 24, "bold", "white")
        time.sleep(3)
        self.num = Text(Point(368, 477.5), "-")
    
    # prolific method that stylizes messages via parameters
    def style(self, num, size, style, color):
        if num == 1:
            self.final_banner.setSize(size)
            self.final_banner.setStyle(style)
            self.final_banner.setTextColor(color)
            self.final_banner.draw(win)
        elif num == 2: 
            self.final_banner_2.setSize(size)
            self.final_banner_2.setStyle(style)
            self.final_banner_2.setTextColor(color)
            self.final_banner_2.draw(win)
    
    # says who goes first
    def start_game(self, color):
        self.final_banner_2.undraw()
        self.final_banner_2 = Text(Point(368, 535), color + " goes first!")
        self.style(2, 24, "bold", "white")
        time.sleep(2)
        self.num = Text(Point(368, 477.5), "-")

    def undraw(self):
        self.final_banner.undraw()
        self.final_banner_2.undraw()
        self.num.undraw()
        
    def undraw_2(self):
        self.final_banner_2.undraw()
    
    # displays a card's value
    def draw(self):
        self.num = Text(Point(368, 477.5), deck.cards[0].get_value())
        self.num.setSize(30)
        self.num.setStyle("bold")
        self.undraw()
        self.num.draw(win)
    
    # displays a card's message
    def draw_message(self):
        self.message = deck.cards[0].get_message()
        self.final_banner = Text(Point(375, 215), self.message)
        if len(self.message) > 45:
            self.final_banner.setSize(14)
        elif 10 <= len(self.message) <= 45:
            self.final_banner.setSize(18)
        elif len(self.message) <= 10:
            self.final_banner.setSize(22)
        self.final_banner.setFill("white")
        self.final_banner.setStyle("bold")
        self.final_banner.draw(win)
    
    # serves an important purpose
    def sorry_banner_2(self, color):
        self.final_banner_2 = Text(Point(368, 535), color + " Player: Don't forget to apologize.")
        self.style(2, 16, "bold", "white")
    
    # displays message when no legal moves are available
    def no_moves(self, color):
        self.final_banner_2.undraw()
        time.sleep(1)
        self.final_banner_2 = Text(Point(368, 535), color + " Player has no legal moves.")
        self.style(2, 16, "bold", "red")
        time.sleep(1.5)
        self.final_banner_2.undraw()

    # displays message when no pieces are in start
    def no_at_start(self, color):
        self.final_banner_2 = Text(Point(368, 535), color + " Player cannot move a piece from start.")
        self.style(2, 16, "bold", "red")
        time.sleep(1.5)
        self.final_banner_2.undraw()
        self.final_banner.undraw()

    # displays a tally of remaining 7 moves
    def seven(self, number, color):
        number = str(number)
        self.final_banner_2.undraw()
        self.final_banner_2 = Text(Point(368, 535), color +  " Player has " + number + " moves left.")
        self.style(2, 16, "bold", "white")
     
    # asks player if he/she wants to move back ward 1 for a 10 
    def ten(self, color):
        self.final_banner_2.undraw()
        self.final_banner_2 = Text(Point(368, 535), color + " Player: Move piece one space backward?")
        self.style(2, 16, "bold", "white")
     
    # asks player if he/she wants to swap pieces for an 11
    def eleven_1(self, color):
        self.final_banner_2.undraw()
        self.final_banner_2 = Text(Point(368, 535), color + " Player: Would you like to swap pieces?")
        self.style(2, 16, "bold", "white")

    # if so, guides player through swap process
    def eleven_swap(self, number, color):
        self.final_banner_2.undraw()
        if number == 1:
            self.final_banner_2 = Text(Point(368, 535), color + " Player: Which opposing piece do you want to switch with?")
            self.style(2, 16, "bold", "white")
        elif number == 2:
            self.final_banner_2 = Text(Point(368, 535), color + " Player: Which of your pieces do you want to switch it with?")
            self.style(2, 16, "bold", "white")
      
    # informs player when AI has no legal moves  
    def ai_no_moves(self, color):
        self.final_banner_2 = Text(Point(368, 535), color + " AI has no legal moves.")
        self.style(2, 16, "bold", "red")
        time.sleep(1.5)
        self.final_banner_2.undraw()
        self.final_banner.undraw()

    # informs player when AI chooses not to move
    def ai_choose_no_moves(self, color):
        self.final_banner_2 = Text(Point(368, 535), color + " AI chose not to move")
        self.style(2, 16, "bold", "red")
        time.sleep(1.5)
        self.final_banner_2.undraw()
        self.final_banner.undraw()

    # asks player if he/she would like to move a piece from start
    def start_move(self, color):
        self.final_banner_2 = Text(Point(368, 535), color + " Player: Move piece out of start?")
        self.style(2, 16, "bold", "white")
     
    # asks player to select a valid piece
    def click(self, color):
        self.final_banner_2.undraw()
        self.final_banner_2 = Text(Point(368, 535), color + " Player: Select a valid piece.")
        self.style(2, 16, "bold", "white")
    
    # "Slide!"
    def slide(self):
        self.final_banner_2.undraw()
        self.final_banner_2 = Text(Point(368, 535), "Slide!")
        self.style(2, 16, "bold", "white")
        time.sleep(1)
        self.final_banner_2.undraw()
    
    # "Extra turn!"
    def extra_turn(self):
        self.final_banner_2.undraw()
        self.final_banner_2 = Text(Point(368, 535), "Extra turn!")
        self.style(2, 16, "bold", "white")
        time.sleep(1)
        self.final_banner_2.undraw()
    
    # informs player of an invalid selection
    def not_valid(self):
        self.final_banner_2.undraw()
        self.final_banner_2 = Text(Point(368, 535), "Invalid selection.")
        self.final_banner_2.setSize(16)
        self.final_banner_2.setFill("red")
        self.final_banner_2.draw(win)
        time.sleep(.5)
        self.final_banner_2.undraw()
    
    # "Green wins!"
    def green_wins(self):
        for i in range(3):
            self.undraw()
            time.sleep(1)
            self.final_banner_2 = Text(Point(375, 535), "Green wins!")
            self.style(2, 20, "bold", "green")
            self.final_banner = Text(Point(375, 215), "Green wins!")
            self.style(1, 20, "bold", "green")
            time.sleep(2)
    
    # "Red wins!"
    def red_wins(self):
        for i in range(3):
            self.undraw()
            time.sleep(1)
            self.final_banner_2 = Text(Point(375, 535), "Red wins!")
            self.style(2, 20, "bold", "red")
            self.final_banner = Text(Point(375, 215), "Red wins!")
            self.style(1, 20, "bold", "red")
            time.sleep(2)
    
    # "Blue wins!"
    def blue_wins(self):
        for i in range(3):
            self.undraw()
            time.sleep(1)
            self.final_banner_2 = Text(Point(375, 535), "Blue wins!")
            self.style(2, 20, "bold", "blue")
            self.final_banner = Text(Point(375, 215), "Blue wins!")
            self.style(1, 20, "bold", "blue")
            time.sleep(2)
    
    # "Yellow wins!"
    def yellow_wins(self):
        for i in range(3):
            self.undraw()
            time.sleep(1)
            self.final_banner_2 = Text(Point(375, 535), "Yellow wins!")
            self.style(2, 20, "bold", "yellow")
            self.final_banner = Text(Point(375, 215), "Yellow wins!")
            self.style(1, 20, "bold", "yellow")
            time.sleep(2)
            
            
# recursive function that calls itself until a player wins
def play_round(player_list):
    for player in player_list:
        if player.play_turn():
            if player.get_color() == "Green":
                status_bar.green_wins()
            elif player.get_color() == "Blue":
                status_bar.blue_wins()
            elif player.get_color() == "Yellow":
                status_bar.yellow_wins()
            elif player.get_color() == "Red":
                status_bar.red_wins()
            return True
        # wait 1 second in between player turns
        time.sleep(1)
    # plays game until a player wins
    return play_round(player_list)

                
def menu():
    # create a start button and wait until it is clicked
    var = True
    while var:
        with VisibleButton(win, Point(750/2, 2*750/3 - 30), 275, 95, "Start Game", "none") as start:
            start.set_label_size(30)
            choice = win.getMouse()
            if start.clicked(choice):
                var = False
    # redraw board so that start button is not left onscreen
    board.undraw()
    board.draw(win)
    game_setup()


def game_setup():
    # create options for players or AIs for each color as well as titles
    Blue = VisibleButton(win, Point(150, 750/3), 65, 35, "Blue:", "Blue")
    Blue_AI = VisibleButton(win, Point(150, 750/3 + 75), 50, 25, "AI", "Blue")
    Blue_Player = VisibleButton(win, Point(150, 750/3 + 150), 50, 25, "Player", "Blue")
    Red = VisibleButton(win, Point(300, 750/3), 65, 35, "Red:", "Red")
    Red_AI = VisibleButton(win, Point(300, 750/3 + 75), 50, 25, "AI", "Red")
    Red_Player = VisibleButton(win, Point(300, 750/3 + 150), 50, 25, "Player", "Red")
    Green = VisibleButton(win, Point(450, 750/3), 65, 35, "Green:", "Green")
    Green_AI = VisibleButton(win, Point(450, 750/3 + 75), 50, 25, "AI", "Green")
    Green_Player = VisibleButton(win, Point(450, 750/3 + 150), 50, 25, "Player", "Green")
    Yellow = VisibleButton(win, Point(600, 750/3), 65, 35, "Yellow:", "Yellow")
    Yellow_AI = VisibleButton(win, Point(600, 750/3 + 75), 50, 25, "AI", "Yellow")
    Yellow_Player = VisibleButton(win, Point(600, 750/3 + 150), 50, 25, "Player", "Yellow")
    confirm = VisibleButton(win, Point(750/2, 2*750/3), 175, 95, "Confirm", "none")
    other_buttons = [Blue, Red, Green, Yellow]
    for button in other_buttons:
        button.activate()
        button.set_label_size(23)
    confirm.activate()
    confirm.set_label_size(30)
    button_list = [Blue_AI, Blue_Player, Red_AI, Red_Player, 
            Green_AI, Green_Player, Yellow_AI, Yellow_Player]
    for button in button_list:
        button.activate()
        button.set_label_size(15)
    while True:
        choice = win.getMouse()
        for button in button_list:
            if button.clicked(choice):
                if button.status():
                    button.deactivate()
                else:
                    button.activate()
        if confirm.clicked(choice):
            color_list = []
            for button in button_list:
                if not button.status():
                    color_list.append(button.get_color())
            # require at least two players or AIs
            if len(color_list) > 1:
                if any(color_list.count(color) > 1 for color in color_list):
                    # make sure that both player and AI were not selected for same color
                    return game_setup()
                while len(button_list) != len(color_list):
                    # delete the buttons that were not selected from button_list
                    for button in button_list:
                        if button.status():
                            del button_list[button_list.index(button)]
                make_game(button_list)


def make_game(button_list):
    # redraw board so that color/player/AI buttons are not left onscreen
    board.undraw()
    board.draw(win)
    card_rectangle.draw(win)
    yes = ChoiceButton(win, Point(750/3 - 40, 750/2), 45, 30, "Yes", "none")
    no = ChoiceButton(win, Point((2*750)/3 + 30, 750/2), 45, 30, "No", "none")
    player_list = []
    # create players based on buttons selected
    for button in button_list:
        if button.get_color() == "Blue":
            if button.get_label() == "Player":
                player_1 = create_player(button.get_color(), yes, no)
            else:
                player_1 = create_AIPlayer(button.get_color())
            player_list.append((player_1))
        elif button.get_color() == "Red":
            if button.get_label() == "Player":
                player_2 = create_player(button.get_color(), yes, no)
            else:
                player_2 = create_AIPlayer(button.get_color())
            player_list.append((player_2))
        elif button.get_color() == "Yellow":
            if button.get_label() == "Player":
                player_3 = create_player(button.get_color(), yes, no)
            else:
                player_3 = create_AIPlayer(button.get_color())
            player_list.append((player_3))
        elif button.get_color() == "Green":
            if button.get_label() == "Player":
                player_4 = create_player(button.get_color(), yes, no)
            else:
                player_4 = create_AIPlayer(button.get_color())
            player_list.append((player_4))
    piece_list = []
    # create a list of all pieces in the game
    for player in player_list:
        piece_list.extend(player.return_pieces())
    # let each player make a list of all rival pieces in game
    for player in player_list:
        player.get_player_pieces(piece_list[:])
    status_bar.start_game(player_list[0].get_color())
    # start playing game
    play_round(player_list)
    return

    
def create_player(color, yes, no):
    return Player(color, deck, win, yes, no)

    
def create_AIPlayer(color):
    return AIPlayer(color, deck, win)


# create global variables that are used in multiple classes (difficult/inefficient to pass them in)
start_location_dictionary = {-1: Point(597, 190), -2: Point(640, 190), -3: 
    Point(597, 240), -4: Point(640, 240), -5: Point(498, 600), -6: 
    Point(545, 600), -7: Point(498, 650), -8: Point(545, 650), -9: 
    Point(90, 505), -10: Point(133, 505), -11: Point(90, 555), -12: 
    Point(133, 555), -13: Point(192, 90), -14: Point(235, 90), -15: 
    Point(192, 140), -16: Point(235, 140)}
green_home_location_dictionary = {"a": Point(375, 105), "b": 
    Point(419, 105), "c": Point(375, 155), "d": Point(419, 155)}
red_home_location_dictionary = {"a": Point(585, 383), "b": 
    Point(629, 383), "c": Point(585, 433), "d": Point(629, 433)}
yellow_home_location_dictionary = {"a": Point(105, 315), "b": 
    Point(149, 315), "c": Point(105, 365), "d": Point(149, 365)}
blue_home_location_dictionary = {"a": Point(316, 590), "b": 
    Point(360, 590), "c": Point(316, 640), "d": Point(360, 640)}
green_safe_location_dictionary = {60: Point(654, 129), 61: 
    Point(610, 129), 62: Point(566, 129), 63: Point(522, 129), 64: Point(478, 129)}
red_safe_location_dictionary = {60: Point(609, 663), 61: 
    Point(609, 618.5), 62: Point(609, 574), 63: Point(609, 529.5), 64: Point(609, 485)}
yellow_safe_location_dictionary = {60: Point(126, 84.5), 61: 
    Point(126, 129), 62: Point(126, 173.5), 63: Point(126, 218), 64: Point(126, 262.5)}
blue_safe_location_dictionary = {60: Point(81, 618.5), 61: 
    Point(125, 618.5), 62: Point(169, 618.5), 63: Point(213, 618.5), 64: Point(257, 618.5)}
win = GraphWin("Sorry!", 750, 750)
board = Image(Point(365, 375), "new_board.gif")
board.draw(win)
time.sleep(.75)
status_bar = Status()
deck = Deck()
deck.shuffle()
card_rectangle = Rectangle(Point(305, 435), Point(430, 520))
card_rectangle.setFill("white")

def main():
    # play game
    #Process(target=Popen(["afplay","apologize.wav"])).start()
    # play music
    Process(target=menu()).start()

if __name__ == "__main__":
    main()