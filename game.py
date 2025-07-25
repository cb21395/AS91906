import arcade
import os

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 780
WINDOW_TITLE = "Platformer"

TILE_SCALING = 1
PLAYER_MOVEMENT_SPEED = 3
GRAVITY = 0.5
PLAYER_JUMP_SPEED = 10
ARCHER_DASH_SPEED = 1

class GameView(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        self.character_sprites = []
        self.current_character_index = 0
        self.player_sprite = None
        self.tile_map = None
        self.scene = None
        self.camera = None
        self.gui_camera = None
        self.score = 0
        self.score_text = None
        self.is_floating = False
        self.float_duration = 2
        self.float_speed = 3
        self.end_of_map = 0
        self.level = 1
        self.reset_score = True
        self.is_climbing = False
        self.climbable_walls = None
        self.map_bottom = 0
        self.archer_dashing = False
        self.archer_dash_on_cd = False
        self.sprite_list = arcade.SpriteList()
        self.walk_animation_index = 0
        self.walk_animation_speed = 0.15  # seconds per frame
        self.time_since_last_frame = 0
        self.knight_direction = 0  # 0 = right, 1 = left
        self.walk_textures_by_character = {}    

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
        characters_path = os.path.join(os.path.dirname(__file__), "characters")
        self.character_sprites = []

        for filename in os.listdir(characters_path):
            if not filename.lower().endswith('.png'):
                continue
            sprite_path = os.path.join(characters_path, filename)
            character_name = os.path.splitext(filename)[0]
            
            sprite = arcade.load_texture(sprite_path)
            idle_textures = {
                "left": []
            }
            left_idle = sprite.flip_left_right() 
            idle_textures["left"].append(left_idle)
            sprite.character_name = character_name
            sprite.center_x = 64
            sprite.center_y = 128
            self.character_sprites.append(sprite)

            # Load walk textures for this character
            textures = self.load_walk_textures(character_name, frame_count=6)
            if textures["right"]:
                self.walk_textures_by_character[character_name] = textures

        self.current_character_index = 0
        self.player_sprite = self.character_sprites[self.current_character_index]

        for sprite in self.character_sprites:
            if sprite.character_name == "knight":
                self.knight_sprite = sprite
            elif sprite.character_name == "archer":
                self.archer_sprite = sprite
            elif sprite.character_name == "wizard":
                self.wizard_sprite = sprite

        self.scene.add_sprite("Player", self.player_sprite)
        textures = self.load_walk_textures(character_name, frame_count=6)
        if textures["right"]:
            self.walk_textures_by_character[character_name] = textures

        self.climbable_walls = self.scene["Climbable"]
        self.danger = self.scene["Danger"]
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, walls=self.scene["Platforms"], gravity_constant=GRAVITY
        )

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        self.background_color = arcade.csscolor.DARK_SLATE_BLUE
        self.end_of_map = (self.tile_map.width * self.tile_map.tile_width) * self.tile_map.scaling

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
        self.gui_camera.use()

    def on_update(self, delta_time):
        #Walking animation logic
        name = self.player_sprite.character_name
        textures = self.walk_textures_by_character.get(name)

        if textures and len(textures["right"]) > 0:
            dx = self.player_sprite.change_x

            if dx < 0:
                direction = "left"
            elif dx > 0:
                direction = "right"
            else:
                direction = "right"  # Default facing direction

            if abs(dx) > 0.1:
                self.time_since_last_frame += delta_time
                if self.time_since_last_frame > self.walk_animation_speed:
                    self.walk_animation_index = (self.walk_animation_index + 1) % len(textures[direction])
                    self.player_sprite.texture = textures[direction][self.walk_animation_index]
                    self.time_since_last_frame = 0
            else:
                self.player_sprite.texture = textures[direction][0]
                self.walk_animation_index = 0
                self.time_since_last_frame = 0



        touching_climbable = self.is_touching_climbable_wall()
        if self.is_climbing and touching_climbable:
            self.player_sprite.center_y += self.player_sprite.change_y
        else:
            self.is_climbing = False
            self.physics_engine.gravity_constant = GRAVITY
            self.physics_engine.update()

        if self.player_sprite.center_y <= self.map_bottom:
            print("Player Sprite's center made contact with bottom of map")
            print(self.player_sprite.center_y)
            self.player_sprite.center_x = 64
            self.player_sprite.center_y = 128
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0

        self.camera.position = self.player_sprite.position
        if arcade.check_for_collision_with_list(self.player_sprite, self.danger):
            self.player_sprite.center_x = 64
            self.player_sprite.center_y = 128
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0

        if self.is_floating:
            self.player_sprite.change_y = 0
            self.player_sprite.center_y += 2.5
            return
        if self.archer_dashing:
            self.player_sprite.change_y = 0
            self.player_sprite.change_x += ARCHER_DASH_SPEED

    def on_key_press(self, key, modifiers):
        touching_climbable = self.is_touching_climbable_wall()
        if key == arcade.key.ESCAPE:
            self.player_sprite.center_x = 64
            self.player_sprite.center_y = 128
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
        if key == arcade.key.Q and not self.is_floating:
            self.switch_player_sprite()
        if key in [arcade.key.UP, arcade.key.W]:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
            elif self.is_climbing:
                self.is_climbing = False
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
        if key in [arcade.key.SPACE]:
            if touching_climbable:
                self.is_climbing = True
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif self.player_sprite == self.archer_sprite and not self.archer_dashing:
                if not self.archer_dash_on_cd:
                    self.start_archer_dash()
            elif self.player_sprite == self.wizard_sprite and self.physics_engine.can_jump():
                self.start_wizard_float()
        if key in [arcade.key.DOWN]:
            if touching_climbable:
                self.is_climbing = False
        if key in [arcade.key.LEFT, arcade.key.A]:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key in [arcade.key.RIGHT, arcade.key.D]:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D]:
            self.player_sprite.change_x = 0
        if key == arcade.key.SPACE and self.is_climbing:
            self.player_sprite.change_y = 0

    def switch_player_sprite(self):
        x = self.player_sprite.center_x
        y = self.player_sprite.bottom
        change_x = self.player_sprite.change_x
        change_y = self.player_sprite.change_y

        self.scene["Player"].remove(self.player_sprite)
        self.current_character_index = (self.current_character_index + 1) % len(self.character_sprites)
        self.player_sprite = self.character_sprites[self.current_character_index]
        self.player_sprite.center_x = x
        self.player_sprite.bottom = y
        self.player_sprite.change_x = change_x
        self.player_sprite.change_y = change_y
        self.scene.add_sprite("Player", self.player_sprite)
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, walls=self.scene["Platforms"], gravity_constant=GRAVITY
        )
        # Set default idle frame
        name = self.player_sprite.character_name
        self.player_sprite.texture = self.walk_textures_by_character[name][0]
        self.walk_animation_index = 0
        self.time_since_last_frame = 0

    def is_touching_climbable_wall(self):
        if self.player_sprite == self.knight_sprite:
            return arcade.check_for_collision_with_list(self.player_sprite, self.climbable_walls)
        return False

    def start_wizard_float(self):
        self.is_floating = True
        arcade.schedule(self.end_wizard_float, self.float_duration)

    def end_wizard_float(self, delta_time):
        self.is_floating = False
        arcade.unschedule(self.end_wizard_float)

    def start_archer_dash(self):
        self.archer_dashing = True
        self.archer_dash_on_cd = True
        arcade.schedule(self.end_archer_dash, 0.5)
        arcade.schedule(self.reset_archer_dash_cooldown, 2.0)

    def end_archer_dash(self, delta_time):
        self.archer_dashing = False
        self.player_sprite.change_x = 0
        arcade.unschedule(self.end_archer_dash)

    def reset_archer_dash_cooldown(self, delta_time):
        self.archer_dash_on_cd = False
        arcade.unschedule(self.reset_archer_dash_cooldown)
    def load_walk_textures(self, character_name, frame_count):
        walk_textures = {
            "right": [],
            "left": []
        }    
        character_path = os.path.join(os.path.dirname(__file__), "characters", character_name)
        for i in range(1, frame_count + 1):
            path = os.path.join(character_path, f"{character_name}_walking{i}.png")
            if not os.path.exists(path):
                continue
            right_texture = arcade.load_texture(path)
            walk_textures["right"].append(right_texture)
            left_texture = right_texture.flip_left_right()
            walk_textures["left"].append(left_texture)
        return walk_textures

def main():
    window = GameView()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
