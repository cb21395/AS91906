import arcade
import os

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 780
WINDOW_TITLE = "Platformer"

TILE_SCALING = 1
PLAYER_MOVEMENT_SPEED = 3
GRAVITY = 0.5
PLAYER_JUMP_SPEED = 11
ARCHER_DASH_SPEED = 15
MAX_HEALTH = 3
DAMAGE_COOLDOWN = 1.0

class Player:
    def __init__(self, characters_path):
        self.character_sprites = []
        self.current_character_index = 0
        self.sprite = None
        self.knight_sprite = None
        self.archer_sprite = None
        self.wizard_sprite = None
        
        self.walk_textures_by_character = {}
        self.walk_animation_index = 0
        self.climb_animation_index = 0
        self.facing_direction = "right"
        self.movement_accumulator = 0
        self.climb_movement_accumulator = 0
        self.movement_threshold = 20
        
        self.is_floating = False
        self.float_duration = 2
        self.float_timer = 0
        
        self.is_climbing = False
        
        self.archer_dashing = False
        self.archer_dash_on_cd = False
        self.dash_timer = 0
        self.dash_cooldown_timer = 0
        
        self.load_characters(characters_path)
        self.max_health = MAX_HEALTH
        self.health = self.max_health
        self.damage_timer = 0
        self.is_invincible = False
        
    def load_characters(self, characters_path):
        for filename in os.listdir(characters_path):
            if not filename.lower().endswith('.png'):
                continue
            sprite_path = os.path.join(characters_path, filename)
            character_name = os.path.splitext(filename)[0]
            
            sprite = arcade.Sprite(sprite_path, scale=TILE_SCALING)
            sprite.character_name = character_name
            sprite.center_x = 64
            sprite.center_y = 128
            self.character_sprites.append(sprite)
            
            textures = self.load_walk_textures(character_name, frame_count=6)
            if textures["right"]:
                self.walk_textures_by_character[character_name] = textures

        self.current_character_index = 0
        self.sprite = self.character_sprites[self.current_character_index]

        for sprite in self.character_sprites:
            if sprite.character_name == "knight":
                self.knight_sprite = sprite
            elif sprite.character_name == "archer":
                self.archer_sprite = sprite
            elif sprite.character_name == "wizard":
                self.wizard_sprite = sprite

        self.load_climbing_textures(characters_path)
    
    def load_walk_textures(self, character_name, frame_count):
        walk_textures = {
            "right": [],
            "left": []
        }    
        character_path = os.path.join(os.path.dirname(__file__), "characters", character_name)
        for i in range(0, frame_count + 1):
            path = os.path.join(character_path, f"{character_name}_walking{i}.png")
            if not os.path.exists(path):
                continue
            right_texture = arcade.load_texture(path)
            walk_textures["right"].append(right_texture)
            left_texture = right_texture.flip_left_right()
            walk_textures["left"].append(left_texture)
        return walk_textures
    
    def load_climbing_textures(self, characters_path):
        climbing_textures = []
        for i in range(1, 3):
            climb_path = os.path.join(characters_path, "knight", f"knight_climbing{i}.png")
            if os.path.exists(climb_path):
                climbing_texture = arcade.load_texture(climb_path)
                climbing_textures.append(climbing_texture)
        
        if "knight" not in self.walk_textures_by_character:
            self.walk_textures_by_character["knight"] = {"right": [], "left": []}
        self.walk_textures_by_character["knight"]["climb"] = climbing_textures
    
    def switch_character(self):
        x = self.sprite.center_x
        y = self.sprite.bottom
        change_x = self.sprite.change_x
        change_y = self.sprite.change_y

        self.current_character_index = (self.current_character_index + 1) % len(self.character_sprites)
        self.sprite = self.character_sprites[self.current_character_index]
        
        self.sprite.center_x = x
        self.sprite.bottom = y
        self.sprite.change_x = change_x
        self.sprite.change_y = change_y
        
        name = self.sprite.character_name
        if name in self.walk_textures_by_character and self.walk_textures_by_character[name]["right"]:
            self.sprite.texture = self.walk_textures_by_character[name][self.facing_direction][0]
        
        self.walk_animation_index = 0
        self.climb_animation_index = 0
        self.movement_accumulator = 0
        self.climb_movement_accumulator = 0
    
    def update_abilities(self, delta_time):
        if self.is_invincible:
            self.damage_timer += delta_time
            if self.damage_timer >= DAMAGE_COOLDOWN:
                self.is_invincible = False
                self.damage_timer = 0
        
        if self.is_floating:
            self.float_timer += delta_time
            if self.float_timer >= self.float_duration:
                self.is_floating = False
                self.float_timer = 0

        if self.archer_dashing:
            self.dash_timer += delta_time
            if self.dash_timer >= 0.5:
                self.archer_dashing = False
                self.sprite.change_x = 0
                self.dash_timer = 0

        if self.archer_dash_on_cd:
            self.dash_cooldown_timer += delta_time
            if self.dash_cooldown_timer >= 2.0:
                self.archer_dash_on_cd = False
                self.dash_cooldown_timer = 0
    
    def update_animations(self, delta_time, is_climbing, touching_climbable, climbable_walls):
        name = self.sprite.character_name
        textures = self.walk_textures_by_character.get(name)
        
        if self.is_invincible:
            flash_rate = 10
            if int(self.damage_timer * flash_rate) % 2:
                self.sprite.alpha = 128
            else:
                self.sprite.alpha = 255
        else:
            self.sprite.alpha = 255
        
        if is_climbing and touching_climbable and self.sprite == self.knight_sprite:
            prev_y = self.sprite.center_y
            
            if self.sprite.change_y > 0:
                test_y = self.sprite.center_y + self.sprite.height // 2 + 2
                
                can_climb_higher = False
                for wall in climbable_walls:
                    if (wall.left <= self.sprite.center_x <= wall.right and
                        wall.bottom <= test_y <= wall.top):
                        can_climb_higher = True
                        break
                
                if can_climb_higher:
                    self.sprite.center_y += self.sprite.change_y
            else:
                self.sprite.center_y += self.sprite.change_y
            
            climb_textures = self.walk_textures_by_character.get("knight", {}).get("climb", [])
            if climb_textures:
                vertical_movement = abs(self.sprite.center_y - prev_y)
                self.climb_movement_accumulator += vertical_movement
                
                if self.climb_movement_accumulator >= self.movement_threshold:
                    self.climb_animation_index = (self.climb_animation_index + 1) % len(climb_textures)
                    self.sprite.texture = climb_textures[self.climb_animation_index]
                    self.climb_movement_accumulator = 0
        else:
            if textures and len(textures["right"]) > 0:
                dx = self.sprite.change_x

                if dx < 0:
                    direction = "left"
                    self.facing_direction = "left"
                elif dx > 0:
                    direction = "right"
                    self.facing_direction = "right"
                else:
                    direction = self.facing_direction

                if abs(dx) > 0.1:
                    self.movement_accumulator += abs(dx)
                    
                    if self.movement_accumulator >= self.movement_threshold:
                        self.walk_animation_index = (self.walk_animation_index + 1) % len(textures[direction])
                        self.sprite.texture = textures[direction][self.walk_animation_index]
                        self.movement_accumulator = 0
                else:
                    self.sprite.texture = textures[direction][0]
                    self.walk_animation_index = 0
                    self.movement_accumulator = 0
    
    def update_movement(self):
        if self.is_floating:
            self.sprite.change_y = 0
            self.sprite.center_y += 2.5
                   
        if self.archer_dashing:
            self.sprite.change_y = 0
            if self.sprite.change_x >= 0:
                self.sprite.change_x = ARCHER_DASH_SPEED
            elif self.sprite.change_x < 0:
                self.sprite.change_x = -ARCHER_DASH_SPEED
        
        return False
    
    def start_wizard_float(self):
        self.is_floating = True
        self.float_timer = 0

    def start_archer_dash(self):
        self.archer_dashing = True
        self.archer_dash_on_cd = True
        self.dash_timer = 0
        self.dash_cooldown_timer = 0
    
    def is_touching_climbable_wall(self, climbable_walls):
        if self.sprite == self.knight_sprite:
            return arcade.check_for_collision_with_list(self.sprite, climbable_walls)
        return False
    
    def reset_position(self):
        self.sprite.center_x = 64
        self.sprite.center_y = 128
        self.sprite.change_x = 0
        self.sprite.change_y = 0
        
    def take_damage(self):
        if not self.is_invincible:
            self.health -= 1
            self.is_invincible = True
            self.damage_timer = 0
            
            if self.health <= 0:
                self.reset_position()
                self.health = self.max_health
                self.is_invincible = False
                self.damage_timer = 0

class GameView(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        self.player = None
        self.tile_map = None
        self.scene = None
        self.camera = None
        self.gui_camera = None
        self.score = 0
        self.score_text = None
        self.end_of_map = 0
        self.level = 1
        self.reset_score = True
        self.climbable_walls = None
        self.map_bottom = 0
        self.physics_engine = None
        self.show_instructions = False
        self.health_bar_list = arcade.SpriteList()
        self.heart_full_texture = None
        self.heart_empty_texture = None

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
        self.player = Player(characters_path)
        
        self.scene.add_sprite("Player", self.player.sprite)
        
        self.climbable_walls = self.scene["Climbable"]
        self.danger = self.scene["Danger"]
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player.sprite, walls=self.scene["Platforms"], gravity_constant=GRAVITY
        )

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        self.background_color = arcade.csscolor.DARK_SLATE_BLUE
        self.end_of_map = (self.tile_map.width * self.tile_map.tile_width) * self.tile_map.scaling
        
        self.setup_health_bar()

    def setup_health_bar(self):
        self.health_bar_list = arcade.SpriteList()
        heart_size = 30
        heart_spacing = 35
        start_x = 20
        start_y = WINDOW_HEIGHT - 40
        
        assets_path = os.path.join(os.path.dirname(__file__), "Assets")
        self.heart_full_texture = arcade.load_texture(os.path.join(assets_path, "heart_full.png"))
        self.heart_empty_texture = arcade.load_texture(os.path.join(assets_path, "heart_empty.png"))
        
        for i in range(self.player.max_health):
            x = start_x + (i * heart_spacing)
            
            full_heart = arcade.Sprite()
            full_heart.texture = self.heart_full_texture
            full_heart.center_x = x
            full_heart.center_y = start_y
            full_heart.scale = heart_size / self.heart_full_texture.width
            full_heart.heart_index = i
            full_heart.is_full = True
            
            empty_heart = arcade.Sprite()
            empty_heart.texture = self.heart_empty_texture
            empty_heart.center_x = x
            empty_heart.center_y = start_y
            empty_heart.scale = heart_size / self.heart_empty_texture.width
            empty_heart.heart_index = i
            empty_heart.is_full = False
            
            self.health_bar_list.append(full_heart)
            self.health_bar_list.append(empty_heart)

    def update_health_display(self):
        for sprite in self.health_bar_list:
            if hasattr(sprite, 'heart_index'):
                if sprite.is_full:
                    sprite.visible = sprite.heart_index < self.player.health
                else:
                    sprite.visible = sprite.heart_index >= self.player.health

    def draw_instructions(self):
        if not self.show_instructions:
            return
            
        arcade.draw_lrbt_rectangle_filled(
            10, 600, WINDOW_HEIGHT - 350, WINDOW_WIDTH - 10,
            (0, 0, 0, 180)
        )
        
        instructions = [
            "CONTROLS:",
            "A/D or Arrows - Move",
            "W/Up - Jump",
            "Q - Switch Characters",
            "",
            "KNIGHT - Space near walls to climb",
            "ARCHER - Space to dash (Careful, it goes far)",
            "WIZARD - Space while grounded to float",
            "",
            "ESC - Reset position",
            "I - Toggle instructions"
        ]
        
        y_start = WINDOW_HEIGHT - 40
        line_height = 22
        
        for i, line in enumerate(instructions):
            if line:
                arcade.draw_text(
                    line,
                    20, y_start - (i * line_height),
                    arcade.color.WHITE, 14,
                    font_name="Arial"
                )

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
        
        self.gui_camera.use()
        self.health_bar_list.draw()
        self.draw_instructions()

    def on_update(self, delta_time):
        self.player.update_abilities(delta_time)
        self.camera.position = self.player.sprite.position
        
        if arcade.check_for_collision_with_list(self.player.sprite, self.danger):
            self.player.take_damage()
            self.update_health_display()
        
        touching_climbable = self.player.is_touching_climbable_wall(self.climbable_walls)
        if self.player.update_movement():
            return
        if self.player.is_climbing and touching_climbable and self.player.sprite == self.player.knight_sprite:
            self.physics_engine.gravity_constant = 0
        else:
            self.player.is_climbing = False
            self.physics_engine.gravity_constant = GRAVITY
            self.physics_engine.update()
        
        self.player.update_animations(delta_time, self.player.is_climbing, touching_climbable, self.climbable_walls)

        if self.player.sprite.center_y <= self.map_bottom:
            self.player.take_damage()
            self.update_health_display()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.I:
            self.show_instructions = not self.show_instructions
            return
            
        touching_climbable = self.player.is_touching_climbable_wall(self.climbable_walls)
        
        if key == arcade.key.ESCAPE:
            self.player.reset_position()
            
        if key == arcade.key.Q and not self.player.is_floating:
            self.switch_player_sprite()
            
        if key in [arcade.key.UP, arcade.key.W]:
            if self.physics_engine.can_jump():
                self.player.sprite.change_y = PLAYER_JUMP_SPEED
            elif self.player.is_climbing:
                self.player.is_climbing = False
                self.player.sprite.change_y = PLAYER_JUMP_SPEED
                
        if key in [arcade.key.SPACE]:
            if touching_climbable:
                self.player.is_climbing = True
                self.player.sprite.change_y = PLAYER_MOVEMENT_SPEED
                climb_textures = self.player.walk_textures_by_character.get("knight", {}).get("climb", [])
                if climb_textures and len(climb_textures) > 0:
                    self.player.climb_animation_index = 0
                    self.player.sprite.texture = climb_textures[0]
            elif self.player.sprite == self.player.archer_sprite and not self.player.archer_dashing:
                if not self.player.archer_dash_on_cd:
                    self.player.start_archer_dash()
            elif self.player.sprite == self.player.wizard_sprite and self.physics_engine.can_jump():
                self.player.start_wizard_float()
                
        if key in [arcade.key.DOWN]:
            if touching_climbable:
                self.player.is_climbing = False
                
        if key in [arcade.key.LEFT, arcade.key.A]:
            self.player.sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key in [arcade.key.RIGHT, arcade.key.D]:
            self.player.sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D]:
            self.player.sprite.change_x = 0
        if key == arcade.key.SPACE and self.player.is_climbing:
            self.player.sprite.change_y = 0

    def switch_player_sprite(self):
        self.scene["Player"].remove(self.player.sprite)
        self.player.switch_character()
        self.scene.add_sprite("Player", self.player.sprite)
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player.sprite, walls=self.scene["Platforms"], gravity_constant=GRAVITY
        )

def main():
    window = GameView()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()