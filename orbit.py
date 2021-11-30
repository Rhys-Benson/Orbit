import arcade
import math
import random as r
import socket
import pickle
import select
from arcade.sprite import Sprite
from arcade.texture import *
from arcade.sprite_list import SpriteList, check_for_collision

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 750
SCREEN_TITLE = "Orbit"

class Player(arcade.Sprite):
    '''
    The Player class is a special sprite that represents that player's character.
    Player has the ability the rotate left and right and accelerate(boost) straight forward in the direction it is facing.
    Player will be reset to the starting position if it strays too far from the edge of the screen.
    '''
    def __init__(self, filename, start_x, start_y, scale=.25):
        super().__init__(filename, scale=scale)
        self.start_x = start_x
        self.start_y = start_y

        self.reset()

        self.booster_accel = .03

    def update(self):
        if self.boosters:
            self.y_velocity += math.sin(math.radians(self.angle + 90)) * self.booster_accel
            self.x_velocity += math.cos(math.radians(self.angle + 90)) * self.booster_accel
        if self.left_pressed:
            self.angle += 5
        if self.right_pressed:
            self.angle -= 5

        self.center_x += self.x_velocity
        self.center_y += self.y_velocity

        if self.center_x <= -200 or self.center_x >= SCREEN_WIDTH + 200 or self.center_y <= -200 or self.center_y >= SCREEN_HEIGHT + 200:
            self.reset()   

    def reset(self):
        self.center_x = self.start_x
        self.center_y = self.start_y
        self.x_velocity = 0
        self.y_velocity = 0
        self.angle = 0
        self.boosters = False
        self.left_pressed = False
        self.right_pressed = False

    def on_key_press(self, key):
        if key == arcade.key.UP or key == arcade.key.W:
            self.boosters = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

    def on_key_release(self, key):
        if key == arcade.key.UP or key == arcade.key.W:
            self.boosters = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        
        
class Planet(arcade.Sprite):
    '''
    A Planet is a special sprite that has a gravitational field that acts on the player.
    The strength and range of gravity is determined by the size(scale) of the Planet.
    Strength of gravity decreases exponentially as distance from the planet is increased, modeled after the gravity formula
    '''

    def __init__(self, filename, scale, x, y):
        super().__init__(filename=filename, scale=scale, center_x=x, center_y=y)

        self.gravity = 300 * scale
        self.range = 300 * math.sqrt(scale)

    def draw(self):
        arcade.draw_circle_filled(self.center_x, self.center_y, self.range, [255,0,0,25])
        super().draw()


    def apply_gravity(self, target):
        dist_x = self.center_x - target.center_x
        dist_y = self.center_y - target.center_y
        dist = math.sqrt(dist_x ** 2 + dist_y ** 2)
        angle = math.atan2(dist_y, dist_x)
        gravity_factor = self.gravity / ((dist / 2) ** 2)


        if dist <= self.range:
            target.x_velocity += math.cos(angle) * gravity_factor
            target.y_velocity += math.sin(angle) * gravity_factor


class LevelView(arcade.View):
    """
    LevelView handles game logic and draws Sprites to the screen
    """

    # A collection of maps defined by planet and goal point locations. More levels will be added in the future.
    # A planet is defined as a tuple with three numbers. (Scale, x-position(percentage), y-position(percentage)).
    level_maps = {
        '0' : {
            'planets' : [(1, .5, .5)],
            'goal' : (SCREEN_WIDTH - 30, SCREEN_HEIGHT - 100),
            'player_start' : (25, 25)
        },
        '1' : {
            'planets' : [
                (1, .5, .5),
                (.66, .83, .25),
                (.75, .2, .66),
                (.5, .18, .2),
                (.33, .75, .58)],
            'goal' : (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100),
            'player_start' : (25, 25)
        },
        '2' : {
            'planets' : [
                (.5, .5, .5),
                (.5, .5, .16),
                (.5, .5, .33),
                (.5, .5, .66),
                (.5, .5, .83),
                (.5, .16, .5),
                (.5, .33, .5),
                (.5, .66, .5),
                (.5, .83, .5)],
            'goal' : (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50),
            'player_start' : (25, 25)
        },
        '3' : {
            'planets' : [
                (3, .1, .9),
                (3, .9, .1),
                (1, .5, .5),
                (.5, .4, .25),
                (.5, .6, .75)
            ],
            'goal' : (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50),
            'player_start' : (25, 25)
        },
        '4' : {
            'planets' : [
                (.5, .2, .5),
                (.5, .2, .16),
                (.5, .2, .33),
                (.5, .2, .66),
                (.5, .2, .83),
                (.5, .5, .58),
                (.5, .5, .24),
                (.5, .5, .41),
                (.5, .5, .74),
                (.5, .5, .91),
                (.5, .5, .08),
                (.5, .8, .5),
                (.5, .8, .16),
                (.5, .8, .33),
                (.5, .8, .66),
                (.5, .8, .83)],
            'goal' : (SCREEN_WIDTH - 30, SCREEN_HEIGHT - 100),
            'player_start' : (25, 25)
        },            
    }

    def __init__(self):
        super().__init__()

        arcade.set_background_color(arcade.color.BLACK)

        self.planet_list = None
        self.player_list = None
        self.planet_image = ":resources:images/space_shooter/meteorGrey_big4.png"
        self.level = 0

    def setup(self):
        '''
        Sets up the game. This function initializes a map based on self.level, and is called
        each time the player passes to the next level.'''
        player_x, player_y = self.level_maps[str(self.level)]['player_start']
        self.player = Player(":resources:images/space_shooter/playerShip1_green.png", player_x, player_y)
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

        planets = [Planet(self.planet_image, p[0], SCREEN_WIDTH * p[1], SCREEN_HEIGHT * p[2]) for p in self.level_maps[str(self.level)]['planets']]
        self.planet_list = SpriteList()
        for planet in planets:
            self.planet_list.append(planet)

        goal_center = self.level_maps[str(self.level)]['goal']
        self.goal = arcade.Sprite(':resources:images/items/flagGreen2.png', scale=.5, center_x=goal_center[0], center_y=goal_center[1])


    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        self.player_list.draw()
        for planet in self.planet_list:
            planet.draw()
        #self.planet_list.draw()
        self.goal.draw()


    def on_update(self, delta_time):
        '''
        Handles logic to move the player, apply gravity from enacting planets, and handle collisions.
        '''

        # Apply gravity to the player for every planet in which the player is in range
        for planet in self.planet_list:
            planet.apply_gravity(self.player)

        self.player_list.update()

        # Restart the level if the player crashes into a planet
        if len(arcade.check_for_collision_with_list(self.player, self.planet_list)) > 0:
            self.player.reset()

        # Load the next level if the player reaches the goal
        if arcade.check_for_collision(self.player, self.goal):
            self.level += 1
            self.setup()


    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.
        """
        self.player.on_key_press(key)
 
    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        self.player.on_key_release(key)

class PartyView(arcade.View):
    '''
    View used to play multiplayer
    maps contains dictionaries representing different maps, listing both player starting locations and planets
    '''

    maps = {
        '1' : {
            'player1_start' : (50, SCREEN_HEIGHT / 2),
            'player2_start' : (SCREEN_WIDTH - 50, SCREEN_HEIGHT / 2),
            'planets' : [(1, .5, .5)]
        }
    }

    def __init__(self, is_host, host_name):
        super().__init__()

        arcade.set_background_color(arcade.color.BLACK)

        self.planet_list = None
        self.player_list = None
        self.send_list = None
        self.planet_image = ":resources:images/space_shooter/meteorGrey_big4.png"
        self.map = 1

        # Connect the host and the client program
        self.is_host = is_host
        self.sock = socket.socket()              
        if self.is_host:
            self.sock.bind((host_name, 12345))
            self.sock.listen(5)
            self.sock, addr = self.sock.accept()
        else:
            self.sock.connect((host_name, 12345))

    def setup(self):
        '''
        Creates sprites for the whole map, including both players and planets
        self.player respresents the character being controlled by the current program
        self.opponent represents the character controlled by the other program
        '''

        # Determine player and opponent variables based on who is the host (player 1)
        if self.is_host:
            player_x, player_y = self.maps[str(self.map)]['player1_start']
            opponent_x, opponent_y = self.maps[str(self.map)]['player2_start']
            player_img = ":resources:images/space_shooter/playerShip1_green.png"
            opponent_img = ":resources:images/space_shooter/playerShip1_orange.png"
        else:
            player_x, player_y = self.maps[str(self.map)]['player2_start']
            opponent_x, opponent_y = self.maps[str(self.map)]['player1_start']
            player_img = ":resources:images/space_shooter/playerShip1_blue.png"
            opponent_img = ":resources:images/space_shooter/playerShip2_orange.png"
    
        self.player = Player(player_img, player_x, player_y)
        self.opponent = Player(opponent_img, opponent_x, opponent_y)

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        self.player_list.append(self.opponent)

        # Create planets
        planets = [Planet(self.planet_image, p[0], SCREEN_WIDTH * p[1], SCREEN_HEIGHT * p[2]) for p in self.maps[str(self.map)]['planets']]
        self.planet_list = SpriteList()
        for planet in planets:
            self.planet_list.append(planet)

        # This allows our communication between processes to be smoother
        self.sock.setblocking(0)


    def on_draw(self):
        ''' Draw both players and planets to the screen'''
        arcade.start_render()

        self.player_list.draw()
        for planet in self.planet_list:
            planet.draw()

    def on_update(self, delta_time: float):
        '''
        Handles game logic for the player
        Send position of player to the other program
        Receive position of opponent from the other program
        '''
        for planet in self.planet_list:
            planet.apply_gravity(self.player)

        self.player_list.update()

        if len(arcade.check_for_collision_with_list(self.player, self.planet_list)) > 0:
            self.player.reset()

        send_data = {
            'center_x' : self.player.center_x,
            'center_y' : self.player.center_y,
            'angle' : self.player.angle
        }

        # Send player's position
        self.sock.sendall(pickle.dumps(send_data))

        # Receive opponent's position
        data = b''
        while True:
            try:
                packet = self.sock.recv(4096)
            except BlockingIOError:
                # break if there is no more to receive
                break
            data += packet
        if data:
            opp_data = pickle.loads(data)
            self.opponent.center_x = opp_data['center_x']
            self.opponent.center_y = opp_data['center_y']
            self.opponent.angle = opp_data['angle']

        
    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.
        """
        self.player.on_key_press(key)
 
    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        self.player.on_key_release(key)
        


def main():
    '''
    Open an arcade window and start the game view.
    '''
    game_mode = input('Select game mode [S/M]: ')
    if game_mode == 'M':
        host_choice = input('Host? [Y/N]')
        if host_choice == 'N':
            host_name = input('Enter name of you host: ')
        else:
            print(f'Host name: {socket.gethostname()}')

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    if game_mode == 'S':
        game = LevelView()
    else: 
        if host_choice == 'Y':
            game = PartyView(True, socket.gethostname())
        else:
            game = PartyView(False, host_name)

    window.show_view(game)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()