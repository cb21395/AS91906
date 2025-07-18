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
        self.end_of_map = 0
        self.level = 1
        self.reset_score = True
        self.is_climbing = False  # <- Climbing flag
        self.climbable_walls = None

        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.gameover_sound = arcade.load_sound(":resources:sounds/gameover1.wav")

    def setup(self):
        layer_options = {
            "Platforms": {"use_spatial_hash": True},
            "Climbable": {"use_spatial_hash": True}
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
        archer_path = os.path.join(FILE_PATH, "ArcherIdle.gif")

        self.player_textures = [
            arcade.load_texture(knight_path),
            arcade.load_texture(archer_path)
        ]

        self.player_sprite = arcade.Sprite(self.player_textures[self.current_texture_index])
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        self.climbable_walls = self.scene["Climbable"]

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, walls=self.scene["Platforms"], gravity_constant=GRAVITY
        )

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        if self.reset_score:
            self.score = 0
        self.reset_score = True

        self.score_text = arcade.Text(f"Score: {self.score}", x=0, y=5)
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

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
        else:
            # Fall back to normal platforming
            self.is_climbing = False
            self.physics_engine.gravity_constant = GRAVITY
            self.physics_engine.update()

        # End of level logic
        if self.player_sprite.center_x >= self.end_of_map:
            self.level += 1
            self.reset_score = False
            self.setup()

        # Camera follows player
        self.camera.position = self.player_sprite.position


    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.setup()
        if key == arcade.key.SPACE:
            self.switch_player_sprite()
        touching_climbable = self.is_touching_climbable_wall()
        if key in [arcade.key.UP, arcade.key.W]:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
            elif touching_climbable:
                self.is_climbing = True
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        if key in [arcade.key.DOWN, arcade.key.S]:
            if touching_climbable:
                self.is_climbing = True
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        if key in [arcade.key.LEFT, arcade.key.A]:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key in [arcade.key.RIGHT, arcade.key.D]:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D]:
            self.player_sprite.change_x = 0

    def switch_player_sprite(self):
        self.current_texture_index = (self.current_texture_index + 1) % len(self.player_textures)
        self.player_sprite.texture = self.player_textures[self.current_texture_index]

    def is_touching_climbable_wall(self):
        return arcade.check_for_collision_with_list(self.player_sprite, self.climbable_walls)


def main():
    window = GameView()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
