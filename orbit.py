import arcade
import math
import random as r

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

    def __init__(self, filename, scale=1):
        super().__init__(filename, scale=scale)
        self.reset()

        self.booster_accel = .025


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
        self.center_x = 25
        self.center_y = 25
        self.x_velocity = 0
        self.y_velocity = 0
        self.angle = 0
        self.boosters = False
        self.left_pressed = False
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

    def draw_range(self):
        arcade.draw_circle_filled(self.center_x, self.center_y, self.range, [255,0,0,25])


    def apply_gravity(self, target):
        dist_x = self.center_x - target.center_x
        dist_y = self.center_y - target.center_y
        dist = math.sqrt(dist_x ** 2 + dist_y ** 2)
        angle = math.atan2(dist_y, dist_x)
        gravity_factor = self.gravity / ((dist / 2) ** 2)


        if dist <= self.range:
            target.x_velocity += math.cos(angle) * gravity_factor
            target.y_velocity += math.sin(angle) * gravity_factor


class GameView(arcade.View):
    """
    GameView handles game logic and draws Sprites to the screen
    """

    # A collection of maps defined by planet and goal point locations. More levels will be added in the future.
    # A planet is defined as a tuple with three numbers. (Scale, x-position(percentage), y-position(percentage)).
    level_maps = {
        '0' : {
            'planets' : [(1, .5, .5)],
            'goal' : (SCREEN_WIDTH - 30, SCREEN_HEIGHT - 100)
        },
        '1' : {
            'planets' : [
                (1, .5, .5),
                (.66, .83, .25),
                (.75, .2, .66),
                (.5, .18, .2),
                (.33, .75, .58)],
            'goal' : (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)},
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
            'goal' : (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50)
        },
        '3' : {
            'planets' : [
                (3, .1, .9),
                (3, .9, .1),
                (1, .5, .5),
                (.5, .4, .25),
                (.5, .6, .75)
            ],
            'goal' : (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50)
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
            'goal' : (SCREEN_WIDTH - 30, SCREEN_HEIGHT - 100)},            
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

        self.player = Player(":resources:images/space_shooter/playerShip1_green.png", scale=.25)
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
            planet.draw_range()
        self.planet_list.draw()
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

        if key == arcade.key.UP:
            self.player.boosters = True
        elif key == arcade.key.LEFT:
            self.player.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.player.right_pressed = True
 
    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        if key == arcade.key.UP:
            self.player.boosters = False
        #elif key == arcade.key.DOWN:
            #self.player.brakes = False
        elif key == arcade.key.LEFT:
            self.player.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.player.right_pressed = False

class TutorialView(arcade.View):
    '''
    A currently experimental view to give the player a tutorial before starting the game.
    '''
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK)

    def on_setup(self):
        ship = arcade.Sprite(":resources:images/space_shooter/playerShip1_green.png", scale=.25, center_x=25, center_y=25)


def main():
    '''
    Open an arcade window and start the game view.
    '''
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game = GameView()
    window.show_view(game)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()