import arcade
import os

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
TILE_SCALING = 1

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 3
GRAVITY = 0.5
PLAYER_JUMP_SPEED = 10
ARCHER_DASH_SPEED = 10

class GameView(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        self.player_textures = []
        self.current_texture_index = 0
        self.player_sprite = None
        self.tile_map = None
        self.scene = None
        self.camera = None
        self.gui_camera = None
        self.score = 0
        self.score_text = None
        self.is_floating = False
        self.float_duration = 1.5
        self.float_speed = 3
        self.end_of_map = 0
        self.level = 1
        self.reset_score = True
        self.is_climbing = False  # <- Climbing flag
        self.climbable_walls = None
        self.map_bottom = 0

    def setup(self):
        layer_options = {
            "Platforms": {"use_spatial_hash": True},
            "Climbable": {"use_spatial_hash": True},
            "Danger": {"use_spatial_hash": True}
        }
        
        map_path = os.path.join(os.path.dirname(__file__), f"Level1.tmx")
        self.tile_map = arcade.load_tilemap(
            map_path,
            scaling=TILE_SCALING,
            layer_options=layer_options,
        )

        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        FILE_PATH = os.path.dirname(os.path.abspath(__file__))
        knight_path = os.path.join(FILE_PATH, "knight.png")
        archer_path = os.path.join(FILE_PATH, "archer.png")
        wizard_path = os.path.join(FILE_PATH, "wizard.png")
        self.knight_sprite = arcade.Sprite(knight_path)
        self.archer_sprite = arcade.Sprite(archer_path)
        self.wizard_sprite = arcade.Sprite(wizard_path)
        self.knight_sprite.center_x = 64
        self.knight_sprite.center_y = 128
        self.player_sprite = self.knight_sprite
        self.scene.add_sprite("Player", self.player_sprite)
        self.climbable_walls = self.scene["Climbable"]
        self.danger = self.scene["Danger"]
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, walls=self.scene["Platforms"], gravity_constant=GRAVITY
        )

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        if self.reset_score:
            self.score = 0
        self.reset_score = True

        self.score_text = arcade.Text(f"Score: {self.score}", x=0, y=5)
        self.background_color = arcade.csscolor.DARK_SLATE_BLUE

        self.end_of_map = (self.tile_map.width * self.tile_map.tile_width) * self.tile_map.scaling
        print(self.end_of_map)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
        self.gui_camera.use()
        self.score_text.draw()

    def on_update(self, delta_time):
        touching_climbable = self.is_touching_climbable_wall()
        if self.is_climbing and touching_climbable:
            # Disable physics engine while climbing
            self.player_sprite.center_y += self.player_sprite.change_y
            self.physics_engine.can_jump == True
            
        else:
            # Fall back to normal platforming
            self.is_climbing = False
            self.physics_engine.gravity_constant = GRAVITY
            self.physics_engine.update()
        if self.player_sprite.center_y <= self.map_bottom:
            self.setup()

        # Camera follows player
        self.camera.position = self.player_sprite.position
        if arcade.check_for_collision_with_list(self.player_sprite, self.danger):
            self.setup()
        if self.is_floating == True:
            self.player_sprite.change_y = 0  # Cancel falling
            self.player_sprite.center_y += 2.5  # Float upward
            return  # Skip gravity and physics

    def on_key_press(self, key, modifiers):
        touching_climbable = self.is_touching_climbable_wall()
        if key == arcade.key.ESCAPE:
            self.setup()
        if key == arcade.key.Q and self.is_floating == False:
            self.switch_player_sprite()
        if key in [arcade.key.UP, arcade.key.W]:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
            elif self.is_climbing == True:
                self.is_climbing = False
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
        if key in [arcade.key.SPACE]:
            if touching_climbable:
                self.is_climbing = True
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif self.player_sprite == self.archer_sprite:
                if self.player_sprite.change_x >= 0:
                    self.player_sprite.change_x = ARCHER_DASH_SPEED
                elif self.player_sprite.change_x < 0:
                    self.player_sprite.change_x = -ARCHER_DASH_SPEED
            elif self.player_sprite == self.wizard_sprite and self.physics_engine.can_jump():
                self.start_wizard_float()

        if key in [arcade.key.DOWN]:
            if touching_climbable:
                self.is_climbing= False
        if key in [arcade.key.LEFT, arcade.key.A]:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key in [arcade.key.RIGHT, arcade.key.D]:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D]:
            self.player_sprite.change_x = 0
        if key in [arcade.key.SPACE]:
            if self.is_climbing == True:
                self.player_sprite.change_y = 0
    def switch_player_sprite(self):
        x = self.player_sprite.center_x
        y = self.player_sprite.center_y
        change_x = self.player_sprite.change_x
        change_y = self.player_sprite.change_y

        # Remove current sprite from scene
        self.scene["Player"].remove(self.player_sprite)

        # Switch sprite
        if self.player_sprite == self.knight_sprite:
            self.player_sprite = self.archer_sprite
        elif self.player_sprite == self.archer_sprite:
            self.player_sprite = self.wizard_sprite
        else: 
            self.player_sprite = self.knight_sprite

        # Apply the saved position and velocity to the new sprite
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y
        self.player_sprite.change_x = change_x
        self.player_sprite.change_y = change_y

        # Add new sprite to scene
        self.scene.add_sprite("Player", self.player_sprite)

        # Update physics engine to use new sprite
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, walls=self.scene["Platforms"], gravity_constant=GRAVITY
        )




    def is_touching_climbable_wall(self):
    # Only allow climbing if current sprite is the knight (index 0)
        if self.player_sprite == self.knight_sprite:
            return arcade.check_for_collision_with_list(self.player_sprite, self.climbable_walls)
        return False
    def start_wizard_float(self):
        self.is_floating = True
        self.input_enabled = False
        arcade.schedule(self.end_wizard_float, 1.5)

    def end_wizard_float(self, delta_time):
        self.is_floating = False
        self.input_enabled = True
        arcade.unschedule(self.end_wizard_float)



def main():
    window = GameView()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
