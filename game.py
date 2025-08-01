"""
RPG Platformer Game

A multi-character platformer game built with Python Arcade
featuring three playable characters:
- Knight: Can climb walls and perform melee attacks
- Archer: Can dash and shoot arrows
- Wizard: Can levitate and cast fire spells

The game includes multiple levels, enemy combat, 
checkpoints, and character-specific abilities.
"""

import arcade
import os

# Window configuration constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 780
WINDOW_TITLE = "RPG Platformer"

# Game scaling and movement constants
TILE_SCALING = 1
ATTACK_SCALING = 2
PLAYER_MOVEMENT_SPEED = 3
GRAVITY = 0.5
PLAYER_JUMP_SPEED = 11
ARCHER_DASH_SPEED = 15

# Health and combat constants
MAX_HEALTH = 3
DAMAGE_COOLDOWN = 1.0
ARROW_SPEED = 8
FIRE_DURATION = 3.0
ATTACK_COOLDOWN = 0.5

# Enemy configuration - maps enemy sprites to their health values
ENEMY_HP = {
    "BoxingGhost.png": 3,
}

# Level enemy configurations
# Format: (sprite_file, x_pos, y_pos, boundary_left, boundary_right, 
# boundary_bottom, boundary_top, speed_x, speed_y)
LEVEL_ENEMIES = {
    1: [
        ("BoxingGhost.png", 300, 200, 200, 400, 200, 200, 0.5, 0.0),
        ("BoxingGhost.png", 3560, 1550, 3560, 3900, 1550, 1700, 
         4.0, 0.0),
        ("BoxingGhost.png", 3700, 1600, 3560, 3900, 1550, 1700, 
         3.0, 2.0),
        ("BoxingGhost.png", 600, 300, 600, 600, 200, 400, 0.0, 1.0),
        ("BoxingGhost.png", 3500, 3000, 2500, 3500, 2950, 3100, 
         4.0, 4.0),
        ("BoxingGhost.png", 3200, 2975, 2500, 3500, 2950, 3100, 
         4.0, 4.0),
        ("BoxingGhost.png", 2800, 3050, 2500, 3500, 2950, 3100, 
         4.0, 4.0),
    ],
    2: [
        ("BoxingGhost.png", 2050, 530, 1900, 2050, 500, 600, 0, 1.5),
        ("BoxingGhost.png", 1750, 550, 1750, 1800, 500, 700, 4, 4.0),
        ("BoxingGhost.png", 2650, 550, 2600, 3050, 500, 700, 
         1.0, 4.0),
        ("BoxingGhost.png", 2450, 550, 2600, 3050, 500, 700, 
         3.0, 2.0),
        ("BoxingGhost.png", 2600, 700, 2600, 3050, 500, 700, 
         4.0, 1.0),
        ("BoxingGhost.png", 3500, 550, 3550, 3650, 550, 750, 
         1.0, 1.0),
        ("BoxingGhost.png", 3350, 600, 3350, 3450, 550, 750, 
         1.0, 1.0),
        ("BoxingGhost.png", 3150, 500, 3150, 3250, 550, 750, 
         1.0, 1.0)
    ],
    3: [
        ("BoxingGhost.png", 2244, 1153, 2350, 2600, 1150, 1250, 2, 2),
        ("BoxingGhost.png", 2000, 1600, 1950, 2600, 1550, 1650, 2, 2),
        ("BoxingGhost.png", 2200, 2000, 2200, 2400, 1980, 2100, 2, 2),
        ("BoxingGhost.png", 2000, 1860, 2000, 2500, 1860, 1860, 4, 0),
        ("BoxingGhost.png", 2000, 1860, 1950, 2600, 1850, 2350, 4, 4),
        ("BoxingGhost.png", 1950, 2000, 1950, 2600, 1850, 2350, 4, 4),
        ("BoxingGhost.png", 2250, 2915, 1950, 2250, 2915, 2915, 4, 0),
        ("BoxingGhost.png", 2250, 4000, 1950, 2400, 3750, 4000, 3, 3),
        ("BoxingGhost.png", 2200, 3780, 1950, 2400, 3750, 4000, 3, 3),
        ("BoxingGhost.png", 2300, 3900, 1950, 2400, 3750, 4000, 4, 3),
        ("BoxingGhost.png", 2380, 3880, 1950, 2400, 3750, 4000, 3, 2),
        ("BoxingGhost.png", 2780, 3640, 2650, 2800, 3640, 3640, 8, 0),
        ("BoxingGhost.png", 1820, 3640, 1820, 1920, 3640, 3640, 8, 0),
    ]
}


class Arrow(arcade.Sprite):
    """
    Arrow projectile fired by the Archer character.

    """
    
    def __init__(self, texture, scale=1.5):
        """
        Initialize an Arrow sprite.
        
        """
        super().__init__()
        self.texture = texture
        self.scale = scale
        self.speed = ARROW_SPEED
        
    def update(self, delta_time=1/60):
        """
        Update arrow position based on its velocity.
        """
        self.center_x += self.change_x
        self.center_y += self.change_y


class Fire(arcade.Sprite):
    """
    Fire spell projectile created by the Wizard character.
    Features flickering animation between two textures 
    and automatic removal after duration.
    """
    
    def __init__(self, texture1, texture2, scale=1.5):
        """
        Initialize a Fire spell sprite.
        """
        super().__init__()
        self.texture1 = texture1
        self.texture2 = texture2
        self.texture = texture1
        self.scale = scale
        self.duration = FIRE_DURATION
        self.timer = 0.0
        self.flicker_timer = 0.0
        self.flicker_rate = 0.15
        self.current_texture = 1
        
    def update(self, delta_time):
        """
        Update fire animation and handle automatic removal.
        """
        # Update main timer
        self.timer += delta_time
        if self.timer >= self.duration:
            self.remove_from_sprite_lists()
            return
        
        # Handle flickering animation between textures
        self.flicker_timer += delta_time
        if self.flicker_timer >= self.flicker_rate:
            if self.current_texture == 1:
                self.texture = self.texture2
                self.current_texture = 2
            else:
                self.texture = self.texture1
                self.current_texture = 1
            self.flicker_timer = 0.0


class KnightSlash(arcade.Sprite):
    """
    Melee attack sprite for the Knight character.
    Automatically removes itself after a short duration.
    """
    
    def __init__(self, texture, scale=2):
        """
        Initialize a Knight slash attack sprite.
        """
        super().__init__()
        self.texture = texture
        self.scale = scale
        self.duration = 0.3  # Short duration for visual effect
        self.timer = 0.0
        
    def update(self, delta_time):
        """
        Update slash timer and handle automatic removal.
        """
        self.timer += delta_time
        if self.timer >= self.duration:
            self.remove_from_sprite_lists()


class Player:
    """
    Main player class managing 
    multiple character sprites and their abilities.
    """
    
    def __init__(self, characters_path):
        """
        Initialize the player with all character sprites and abilities.
        """
        # Character management
        self.character_sprites = []
        self.current_character_index = 0
        self.sprite = None
        self.knight_sprite = None
        self.archer_sprite = None
        self.wizard_sprite = None
        
        # Animation system
        self.walk_textures_by_character = {}
        self.attack_textures_by_character = {}
        self.walk_animation_index = 0
        self.climb_animation_index = 0
        self.facing_direction = "right"
        self.movement_accumulator = 0
        self.climb_movement_accumulator = 0
        self.movement_threshold = 20
        
        # Wizard floating ability
        self.is_floating = False
        self.float_duration = 2
        self.float_timer = 0
        
        # Knight climbing ability
        self.is_climbing = False
        
        # Archer dashing ability
        self.archer_dashing = False
        self.archer_dash_on_cd = False
        self.dash_timer = 0
        self.dash_direction = 1
        self.dash_cooldown_timer = 0

        # Combat system
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_cooldown_timer = 0
        self.attack_on_cooldown = False
        
        # Health and spawning
        self.spawn_x = 40
        self.spawn_y = 200
        self.load_characters(characters_path)
        self.max_health = MAX_HEALTH
        self.health = self.max_health
        self.damage_timer = 0
        self.is_invincible = False
        
    def load_characters(self, characters_path):
        """
        Load all character sprites and their
        textures from the characters directory.
        """
        # Load character sprites from PNG files
        for filename in os.listdir(characters_path):
            if not filename.lower().endswith('.png'):
                continue
            sprite_path = os.path.join(characters_path, filename)
            character_name = os.path.splitext(filename)[0]
            
            # Create sprite and set initial properties
            sprite = arcade.Sprite(sprite_path, scale=TILE_SCALING)
            sprite.character_name = character_name
            sprite.center_x = self.spawn_x
            sprite.center_y = self.spawn_y
            self.character_sprites.append(sprite)
            
            # Load walking animation textures
            textures = self.load_walk_textures(character_name, frame_count=6)
            if textures["right"]:
                self.walk_textures_by_character[character_name] = textures
            
            # Load attack textures
            attack_textures = self.load_attack_textures(character_name)
            if attack_textures:
                self.attack_textures_by_character[character_name] = (
                attack_textures)

        # Set initial character
        self.current_character_index = 0
        self.sprite = self.character_sprites[self.current_character_index]

        # Store references to specific character sprites for easy access
        for sprite in self.character_sprites:
            if sprite.character_name == "knight":
                self.knight_sprite = sprite
            elif sprite.character_name == "archer":
                self.archer_sprite = sprite
            elif sprite.character_name == "wizard":
                self.wizard_sprite = sprite

        # Load climbing textures (knight-specific)
        self.load_climbing_textures(characters_path)
    
    def load_walk_textures(self, character_name, frame_count):
        """
        Load walking animation textures for a character.
        """
        walk_textures = {
            "right": [],
            "left": []
        }    
        character_path = os.path.join(os.path.dirname(__file__), 
        "characters", character_name)
        
        # Load each frame of the walking animation
        for i in range(0, frame_count + 1):
            path = os.path.join(character_path,
            f"{character_name}_walking{i}.png")
            if not os.path.exists(path):
                continue
            # Load right-facing texture and 
            # create left-facing by flipping
            right_texture = arcade.load_texture(path)
            walk_textures["right"].append(right_texture)
            left_texture = right_texture.flip_left_right()
            walk_textures["left"].append(left_texture)
        return walk_textures
    
    def load_attack_textures(self, character_name):
        """
        Load attack textures for a character. 
        Each character has different attack patterns.
        """
        attack_textures = {}
        character_path = os.path.join(os.path.dirname(__file__),
        "characters", character_name)
        
        if character_name == "knight":
            # Knight has single attack texture
            attack_path = os.path.join(character_path, 
            "knight_attack1.png")
            if os.path.exists(attack_path):
                right_texture = arcade.load_texture(attack_path)
                left_texture = right_texture.flip_left_right()
                attack_textures = {
                    "right": right_texture,
                    "left": left_texture
                }
        elif character_name == "archer":
            # Archer has single attack texture (bow drawing)
            attack_path = os.path.join(character_path,
            "archer_attack1.png")
            if os.path.exists(attack_path):
                right_texture = arcade.load_texture(attack_path)
                left_texture = right_texture.flip_left_right()
                attack_textures = {
                    "right": right_texture,
                    "left": left_texture
                }
        elif character_name == "wizard":
            # Wizard has two attack textures for fire animation
            attack_path1 = os.path.join(character_path, 
            "wizard_attack1.png")
            attack_path2 = os.path.join(character_path, 
            "wizard_attack2.png")
            
            if os.path.exists(attack_path1) and os.path.exists(attack_path2):
                right_texture1 = arcade.load_texture(attack_path1)
                left_texture1 = right_texture1.flip_left_right()
                
                right_texture2 = arcade.load_texture(attack_path2)
                left_texture2 = right_texture2.flip_left_right()
                
                attack_textures = {
                    "right": (right_texture1, right_texture2),
                    "left": (left_texture1, left_texture2)
                }
        
        return attack_textures
        
    def load_climbing_textures(self, characters_path):
        """
        Load climbing animation textures for the knight character.
        """
        climbing_textures = []
        for i in range(1, 3):
            climb_path = os.path.join(characters_path, "knight",
            f"knight_climbing{i}.png")
            if os.path.exists(climb_path):
                climbing_texture = arcade.load_texture(climb_path)
                climbing_textures.append(climbing_texture)
        
        # Add climbing textures to knight's texture dictionary
        if "knight" not in self.walk_textures_by_character:
            self.walk_textures_by_character["knight"] = {"right": [],
            "left": []}
        self.walk_textures_by_character["knight"]["climb"] = climbing_textures
    
    def switch_character(self):
        """
        Switch to the next character in the rotation while
        preserving position and velocity.
        """
        # Store current character state
        x = self.sprite.center_x
        y = self.sprite.bottom
        change_x = self.sprite.change_x
        change_y = self.sprite.change_y

        # Switch to next character
        self.current_character_index = (
        self.current_character_index + 1
        ) % len(self.character_sprites)
        self.sprite = self.character_sprites[self.current_character_index]
        
        # Restore position and velocity
        self.sprite.center_x = x
        self.sprite.bottom = y
        self.sprite.change_x = change_x
        self.sprite.change_y = change_y
        
        # Set appropriate texture for new character
        name = self.sprite.character_name
        if name in self.walk_textures_by_character and (
            self.walk_textures_by_character[name]["right"]):
            self.sprite.texture = (
            self.walk_textures_by_character[name][self.facing_direction][0])
        
        # Reset animation and combat states
        self.walk_animation_index = 0
        self.climb_animation_index = 0
        self.movement_accumulator = 0
        self.climb_movement_accumulator = 0
        self.is_attacking = False
        self.attack_timer = 0
    
    def update_abilities(self, delta_time):
        """
        Update all character abilities and their timers.
        """
        # Update invincibility after taking damage
        if self.is_invincible:
            self.damage_timer += delta_time
            if self.damage_timer >= DAMAGE_COOLDOWN:
                self.is_invincible = False
                self.damage_timer = 0
        
        # Update wizard floating ability
        if self.is_floating:
            self.float_timer += delta_time
            if self.float_timer >= self.float_duration:
                self.is_floating = False
                self.float_timer = 0

        # Update archer dashing ability
        if self.archer_dashing:
            self.dash_timer += delta_time
            if self.dash_timer >= 0.5:
                self.archer_dashing = False
                self.sprite.change_x = 0
                self.dash_timer = 0

        # Update archer dash cooldown
        if self.archer_dash_on_cd:
            self.dash_cooldown_timer += delta_time
            if self.dash_cooldown_timer >= 2.0:
                self.archer_dash_on_cd = False
                self.dash_cooldown_timer = 0
                
        # Update attack animation
        if self.is_attacking:
            self.attack_timer += delta_time
            if self.attack_timer >= 0.3:
                self.is_attacking = False
                self.attack_timer = 0
                self.attack_on_cooldown = True
                self.attack_cooldown_timer = 0
                # Reset to normal texture after attack
                name = self.sprite.character_name
                if name in self.walk_textures_by_character and (
                self.walk_textures_by_character[name]["right"]):
                    self.sprite.texture = (
                    self.walk_textures_by_character[name]
                    [self.facing_direction][0])
                
        # Update attack cooldown
        if self.attack_on_cooldown:
            self.attack_cooldown_timer += delta_time
            if self.attack_cooldown_timer >= ATTACK_COOLDOWN:
                self.attack_on_cooldown = False
                self.attack_cooldown_timer = 0
    
    def update_animations(self, delta_time, is_climbing, touching_climbable,
    climbable_walls):
        """
        Update character animations based on movement and state.
        """
        name = self.sprite.character_name
        textures = self.walk_textures_by_character.get(name)
        
        # Handle invincibility flashing effect
        if self.is_invincible:
            flash_rate = 10
            if int(self.damage_timer * flash_rate) % 2:
                self.sprite.alpha = 128  # Semi-transparent
            else:
                self.sprite.alpha = 255  # Fully opaque
        else:
            self.sprite.alpha = 255
        
        # Handle climbing animation (knight only)
        if is_climbing and touching_climbable and (
        self.sprite == self.knight_sprite):
            prev_y = self.sprite.center_y
            
            # Check if can climb higher when moving up
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
            
            # Update climbing animation based on vertical movement
            climb_textures = (
            self.walk_textures_by_character.get("knight", {}).get("climb", []))
            if climb_textures:
                vertical_movement = abs(self.sprite.center_y - prev_y)
                self.climb_movement_accumulator += vertical_movement
                
                if self.climb_movement_accumulator >= self.movement_threshold:
                    self.climb_animation_index = (
                    (self.climb_animation_index + 1)
                    % len(climb_textures))
                    self.sprite.texture = (climb_textures
                    [self.climb_animation_index])
                    self.climb_movement_accumulator = 0
        else:
            # Handle normal walking animation
            if textures and len(textures["right"]) > 0:
                dx = self.sprite.change_x

                # Determine facing direction based on movement
                if dx < 0:
                    direction = "left"
                    self.facing_direction = "left"
                elif dx > 0:
                    direction = "right"
                    self.facing_direction = "right"
                else:
                    direction = self.facing_direction

                # Update animation if moving
                if abs(dx) > 0.1:
                    self.movement_accumulator += abs(dx)
                    
                    if self.movement_accumulator >= self.movement_threshold:
                        self.walk_animation_index = (
                        self.walk_animation_index + 1
                        ) % len(textures[direction])

                        self.sprite.texture = (textures[direction]
                        [self.walk_animation_index])
                        self.movement_accumulator = 0
                else:
                    # Standing still - use first frame
                    self.sprite.texture = textures[direction][0]
                    self.walk_animation_index = 0
                    self.movement_accumulator = 0
    
    def is_touching_climbable_wall(self, climbable_walls):
        """
        Check if the knight character is touching a climbable wall.
        """
        if self.sprite == self.knight_sprite:
            return arcade.check_for_collision_with_list(self.sprite, climbable_walls)
        return False

    def reset(self):
        """
        Reset player to spawn position and clear all states.
        """
        self.sprite.center_x = self.spawn_x
        self.sprite.center_y = self.spawn_y
        self.sprite.change_x = 0
        self.sprite.change_y = 0
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_on_cooldown = False
        self.attack_cooldown_timer = 0
    
    def update_movement(self):
        """
        Update special movement abilities (floating and dashing).
        """
        # Handle wizard floating
        if self.is_floating:
            self.sprite.change_y = 0
            self.sprite.center_y += 2.5
               
        # Handle archer dashing
        if self.archer_dashing:
            self.sprite.change_y = 0
            self.sprite.change_x = ARCHER_DASH_SPEED * self.dash_direction
        
        return False
    
    def start_wizard_float(self):
        """
        Start the wizard's floating ability.
        """
        self.is_floating = True
        self.float_timer = 0

    def start_archer_dash(self, direction=None):
        """
        Start the archer's dash ability.
        """
        self.archer_dashing = True
        self.archer_dash_on_cd = True
        self.dash_timer = 0
        self.dash_cooldown_timer = 0
        if direction is None:
            self.dash_direction = 1 if self.facing_direction == "right" else -1
        else:
            self.dash_direction = direction
    
    def perform_attack(self):
        """
        Perform an attack based on the current character.
        """
        if self.attack_on_cooldown or self.is_attacking:
            return None
            
        self.is_attacking = True
        self.attack_timer = 0
        
        character_name = self.sprite.character_name
        
        # Create appropriate attack based on character
        if character_name == "knight":
            return self.create_knight_slash()
        elif character_name == "archer":
            return self.create_archer_arrow()
        elif character_name == "wizard":
            return self.create_wizard_fire()
            
        return None
    
    def create_knight_slash(self):
        """
        Create a knight slash attack sprite.
        """
        if "knight" not in self.attack_textures_by_character:
            return None
            
        slash_texture = (self.attack_textures_by_character["knight"]
        [self.facing_direction])
        slash = KnightSlash(slash_texture, scale=ATTACK_SCALING)
        
        # Position slash in front of knight
        offset_x = 20 if self.facing_direction == "right" else -20
        slash.center_x = self.sprite.center_x + offset_x
        slash.center_y = self.sprite.center_y
        
        return slash
    
    def create_archer_arrow(self):
        """
        Creates an arrow projectile for the archer character.
        """
        # Check if archer attack textures are loaded
        if "archer" not in self.attack_textures_by_character:
            return None
            
        # Get the appropriate arrow texture based on facing direction
        arrow_texture = (self.attack_textures_by_character["archer"]
        [self.facing_direction])
        arrow = Arrow(arrow_texture, scale=ATTACK_SCALING)
        
        # Position arrow slightly offset from 
        # player center based on facing direction
        offset_x = 10 if self.facing_direction == "right" else -10
        arrow.center_x = self.sprite.center_x + offset_x
        arrow.center_y = self.sprite.center_y
        
        # Set arrow velocity (horizontal movement only)
        arrow.change_x = (
            ARROW_SPEED
            if self.facing_direction == "right"
            else -ARROW_SPEED
        )
        arrow.change_y = 0
        
        return arrow

    def create_wizard_fire(self):
        """
        Creates a fire attack for the wizard character.
        """
        # Check if wizard attack textures are loaded
        if "wizard" not in self.attack_textures_by_character:
            print("Warning: Wizard attack textures not loaded")
            return None
            
        # Get fire textures (tuple of two textures for animation)
        fire_textures = self.attack_textures_by_character["wizard"][self.facing_direction]
        
        # Debug print to check texture loading
        print(f"Fire textures type: {type(fire_textures)}")
        print(f"Fire textures content: {fire_textures}")
        
        # Handle the tuple of textures properly
        if isinstance(fire_textures, tuple) and len(fire_textures) >= 2:
            fire = Fire(fire_textures[0], fire_textures[1], scale=ATTACK_SCALING)
        else:
            print("Error: Fire textures not in expected tuple format")
            return None
        
        # Position fire with larger offset and slight vertical adjustment
        offset_x = 25 if self.facing_direction == "right" else -25
        offset_y = -5
        fire.center_x = self.sprite.center_x + offset_x
        fire.center_y = self.sprite.center_y + offset_y
        
        print(f"Fire created at position: ({fire.center_x}, {fire.center_y})")
        
        return fire

    def take_damage(self):
        """
        Handles player taking damage, including invincibility frames
        and death/respawn logic.
        Reduces health by 1 and triggers invincibility period
        to prevent rapid damage.
        """
        # Only take damage if not currently invincible
        if not self.is_invincible:
            self.health -= 1
            self.is_invincible = True 
            self.damage_timer = 0      
            
            # Handle player death
            if self.health <= 0:
                self.reset()                    
                self.health = self.max_health   
                self.is_invincible = False      
                self.damage_timer = 0          

    def set_spawn_point(self, x, y):
        """
        Sets the player's spawn point coordinates for respawning after death.
        """
        self.spawn_x = x
        self.spawn_y = y

class Enemy(arcade.Sprite):
    """
    Enemy sprite class that handles movement, health, damage,
    and boundary constraints.
    """
    
    def __init__(self, image_path, scale=TILE_SCALING):
        """
        Initialize an enemy sprite with movement,
        health, and visual properties.
        """
        super().__init__(image_path, scale)
        
        # Movement properties
        self.speed_x = 0   # Horizontal movement speed
        self.speed_y = 0   # Vertical movement speed
        self.change_x = self.speed_x
        self.change_y = self.speed_y
        
        # Default movement boundaries (can be overridden per enemy)
        self.boundary_left = 0
        self.boundary_right = 0
        self.boundary_top = 0
        self.boundary_bottom = 0
        
        # Health system based on enemy type
        filename = os.path.basename(image_path)
        # Get HP from config or default to 1
        self.max_hp = ENEMY_HP.get(filename, 1)  
        self.current_hp = self.max_hp
        
        # Damage visualization system
        self.damage_flash_timer = 0
        self.is_flashing = False
        
    def update(self, delta_time=1/60):
        """
        Update enemy position, handle boundary collisions,
        and manage damage flash effects.
        """
        # Update position based on velocity
        self.center_x += self.change_x
        self.center_y += self.change_y
        
        # Handle horizontal boundary collisions (reverse direction 
        # when hitting walls)
        if self.center_x >= self.boundary_right and self.change_x > 0:
            self.change_x = -abs(self.speed_x)  # Move left
        elif self.center_x <= self.boundary_left and self.change_x < 0:
            self.change_x = abs(self.speed_x)   # Move right
            
        # Handle vertical boundary collisions
        # (for flying/jumping enemies)
        if self.center_y >= self.boundary_top and self.change_y > 0:
            self.change_y = -abs(self.speed_y)  # Move down
        elif self.center_y <= self.boundary_bottom and self.change_y < 0:
            self.change_y = abs(self.speed_y)   # Move up
            
        # Handle damage flash animation
        if self.is_flashing:
            self.damage_flash_timer += delta_time
            if self.damage_flash_timer >= 0.3:  # Flash duration
                # End flashing effect
                self.is_flashing = False
                self.damage_flash_timer = 0
                self.alpha = 255  # Full opacity
            else:
                # Create flashing effect by alternating transparency
                flash_rate = 20  # How fast the flashing occurs
                if int(self.damage_flash_timer * flash_rate) % 2:
                    self.alpha = 128  # Semi-transparent
                else:
                    self.alpha = 255  # Full opacity
    
    def take_damage(self, damage=1):
        """
        Apply damage to the enemy and trigger visual feedback.
        """
        self.current_hp -= damage
        self.is_flashing = True      # Start damage flash effect
        self.damage_flash_timer = 0  # Reset flash timer
        
        # Return True if enemy should be destroyed
        if self.current_hp <= 0:
            return True 
        return False
    
    def draw_hp_bar(self):
        """
        Draw a health bar above the enemy when damaged.
        Only displays when enemy has taken damage (current_hp < max_hp).
        """
        if self.current_hp < self.max_hp:
            # Health bar dimensions and positioning
            bar_width = 30
            bar_height = 4
            # Center horizontally above enemy
            bar_x = self.center_x - bar_width // 2  
            # Position above enemy sprite
            bar_y = self.center_y + self.height // 2 + 10  
            
            # Draw red (represents missing health)
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + bar_width,
                bar_y, bar_y + bar_height,
                arcade.color.RED
            )
            
            # Draw green foreground (represents current health)
            health_percentage = self.current_hp / self.max_hp
            health_width = bar_width * health_percentage
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + health_width,
                bar_y, bar_y + bar_height,
                arcade.color.GREEN
            )

class GameView(arcade.Window):
    """
    Main game window class that manages the entire game state,
    including player, enemies,
    level progression, UI elements, and game logic.
    """
    
    def __init__(self):
        """window and all game state variables."""
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
        
        # Core game objects
        self.player = None
        self.tile_map = None
        self.scene = None
        
        # Camera system
        self.camera = None      # World camera (follows player)
        self.gui_camera = None  # UI camera (stays fixed)
        
        # Game state variables
        self.score = 0
        self.score_text = None
        self.end_of_map = 0
        self.level = 1
        self.reset_score = True
        self.map_bottom = 0
        self.show_instructions = True
        self.game_won = False
        
        # Level-specific sprite lists
        self.climbable_walls = None
        self.checkpoints = None
        self.activated_checkpoints = set()
        self.enemies = arcade.SpriteList()
        self.exits = None 
        
        # Attack/projectile sprite lists
        self.knight_attacks = arcade.SpriteList()
        self.archer_arrows = arcade.SpriteList()
        self.wizard_fires = arcade.SpriteList()
        
        # Physics engine
        self.physics_engine = None
        
        # UI elements
        self.health_bar_list = arcade.SpriteList()
        self.heart_full_texture = None
        self.heart_empty_texture = None
        
    def setup(self):
        """
        Initialize the game level, load map, setup player,
        enemies, and physics.
        Called when starting a new level or restarting the game.
        """
        # Define which map layers require collision detection
        layer_options = {
            "Platforms": {"use_spatial_hash": True},  
            "Climbable": {"use_spatial_hash": True},  
            "Danger": {"use_spatial_hash": True},     
            "Exit": {"use_spatial_hash": True},       
            "Start": {"use_spatial_hash": True}      
        }
        # Load the Tiled map file for the current level
        map_path = os.path.join(os.path.dirname(__file__),
        f"Level{self.level}.tmx")
        self.tile_map = arcade.load_tilemap(
            map_path,
            scaling=TILE_SCALING,
            layer_options=layer_options,
        )
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        
        # Initialize player with character assets
        characters_path = os.path.join(os.path.dirname(__file__), 
        "characters")
        self.player = Player(characters_path)
        
        # Set player spawn point from map data
        self.set_player_spawn_from_start_layer()
        
        # Add player to the scene
        self.scene.add_sprite("Player", self.player.sprite)
        
        # Assign map layers to appropriate variables for game logic
        self.climbable_walls = self.scene["Climbable"]
        self.danger = self.scene["Danger"]
        
        # Handle optional map layers (some levels may not have these)
        if "Exit" in self.scene:
            self.exits = self.scene["Exit"]
        else:
            self.exits = arcade.SpriteList()

        if "Checkpoint" in self.scene:
            self.checkpoints = self.scene["Checkpoint"]
        else:
            self.checkpoints = arcade.SpriteList()
        
        # Setup enemies for this level
        self.setup_enemies()
        
        # Initialize physics engine for platformer movement
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player.sprite, walls=self.scene["Platforms"], 
            gravity_constant=GRAVITY
        )

        # Setup camera system
        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        self.background_color = arcade.csscolor.DARK_SLATE_BLUE
        
        # Calculate map boundaries
        self.end_of_map = (self.tile_map.width * 
        self.tile_map.tile_width) * self.tile_map.scaling
        
        # Setup UI elements
        self.setup_health_bar()

    def set_player_spawn_from_start_layer(self):
        """
        Find the start position marker in the map 
        and set player spawn point there.
        Uses the "Start" layer from the Tiled map to 
        determine spawn coordinates.
        """
        if "Start" in self.scene:
            start_sprites = self.scene["Start"]
            if len(start_sprites) > 0:
                start_sprite = start_sprites[0]
                spawn_x = start_sprite.center_x
                spawn_y = start_sprite.center_y
                
                # Set spawn point and move player there
                self.player.set_spawn_point(spawn_x, spawn_y)
                self.player.sprite.center_x = spawn_x
                self.player.sprite.center_y = spawn_y

    def switch_to_next_level(self):
        """
        Progress to the next level if available.
        Resets player velocity and reinitializes 
        the game with new level data.
        """
        if self.level < 3:  # Maximum of 3 levels
            self.level += 1
            # Stop player movement before switching
            self.player.sprite.change_x = 0
            self.player.sprite.change_y = 0
            self.setup()  # Reinitialize with new level
        
    def setup_enemies(self):
        """
        Initialize all enemies for 
        the current level based on configuration data.
        Sets up enemy positions, movement boundaries,
        and behavior patterns.
        """
        self.enemies = arcade.SpriteList()
        
        # Path to enemy sprite assets
        assets_path = os.path.join(os.path.dirname(__file__),
        "assets")
        
        # Get enemy configuration for current level
        enemy_configs = LEVEL_ENEMIES.get(self.level, [])
        
        if not enemy_configs:
            print(
            f"Warning: No enemy configuration found for level {self.level}")
            return
        
        # Create each enemy from configuration data
        for (monster_file, x_pos, y_pos, boundary_left, boundary_right,
        boundary_bottom, boundary_top, speed_x, speed_y) in enemy_configs:
            enemy = Enemy(os.path.join(assets_path, monster_file))
            
            # Set initial position
            enemy.center_x = x_pos
            enemy.center_y = y_pos
            
            # Set movement boundaries for AI patrolling
            enemy.boundary_left = boundary_left
            enemy.boundary_right = boundary_right
            enemy.boundary_bottom = boundary_bottom
            enemy.boundary_top = boundary_top
            
            # Set movement speeds
            enemy.speed_x = speed_x
            enemy.speed_y = speed_y
            enemy.change_x = speed_x
            enemy.change_y = speed_y
            
            self.enemies.append(enemy)
            
    def setup_health_bar(self):
        """
        Create visual health display using heart sprites.
        Sets up both full and empty heart textures
        for each health point.
        """
        self.health_bar_list = arcade.SpriteList()
        
        # Health bar display parameters
        heart_size = 30
        heart_spacing = 35
        start_x = 20
        start_y = WINDOW_HEIGHT - 40
        
        # Load heart textures
        assets_path = os.path.join(os.path.dirname(__file__), "Assets")
        self.heart_full_texture = arcade.load_texture(os.path.join(
        assets_path, "heart_full.png"))
        self.heart_empty_texture = arcade.load_texture(os.path.join(
        assets_path, "heart_empty.png"))
        
        # Create heart sprites for each health point
        for i in range(self.player.max_health):
            x = start_x + (i * heart_spacing)
            
            # Full heart sprite (shown when player has this health point)
            full_heart = arcade.Sprite()
            full_heart.texture = self.heart_full_texture
            full_heart.center_x = x
            full_heart.center_y = start_y
            full_heart.scale = heart_size / self.heart_full_texture.width
            full_heart.heart_index = i
            full_heart.is_full = True
            
            # Empty heart sprite (shown when player is missing 
            # this health point)
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
        """
        Update the visual health bar to reflect current player health.
        Shows/hides full and empty hearts based on current health value.
        """
        for sprite in self.health_bar_list:
            if hasattr(sprite, 'heart_index'):
                if sprite.is_full:
                    # Show full hearts for health points 
                    # the player still has
                    sprite.visible = sprite.heart_index < self.player.health
                else:
                    # Show empty hearts for health points 
                    # the player has lost
                    sprite.visible = sprite.heart_index >= self.player.health

    def draw_instructions(self):
        """
        Draw the instruction overlay showing game controls 
        and character abilities. Only displays when show_instructions is
        True.
        """
        if not self.show_instructions:
            return
            
        # Draw semi-transparent background for instructions
        arcade.draw_lrbt_rectangle_filled(
            10, 650, WINDOW_HEIGHT - 400, WINDOW_WIDTH - 10,
            (0, 0, 0, 180)  # Black with transparency
        )
        
        # Instruction text content
        instructions = [
            "CONTROLS:",
            "A/D or Arrows - Move",
            "W/Up - Jump",
            "1 - Switch to Archer",
            "2 - Switch to Knight",
            "3 - Switch to Wizard",
            "E - Attack",   
            "Space - Character Specific Ability.",
            "KNIGHT - Ability: Climb, Attack: Forward Slash",
            "ARCHER - Ability: Dash, Attack: Arrow Shoot",
            "WIZARD - Ability: Levitate, Attack: Firey Terrain",
            "Hint 1: You can only levitate while your on the ground.",
            "Hint 2: You can't fall while Dashing",
            "Hint 3: You won't fall if your climbing on a wall.",
            "Bonus Hint: Kill all the enemies on level 3 to win!",
            "ESC - Reset position",
            "I - Toggle instructions",
        ]
        
        # Draw each instruction line
        y_start = WINDOW_HEIGHT - 40
        line_height = 22
        
        for i, line in enumerate(instructions):
            if line:  # Skip empty lines
                arcade.draw_text(
                    line,
                    20, y_start - (i * line_height),
                    arcade.color.WHITE, 14,
                    font_name="Arial"
                )

    def on_draw(self):
        """
        Render all game elements to the screen.
        """
        self.clear()
        
        # Check for victory condition
        if self.game_won:
            arcade.draw_text(
                "VICTORY!",
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT // 2,
                arcade.color.YELLOW,
                font_size=72,
                anchor_x="center",
                anchor_y="center",
                bold=True,
            )
            return 
            
        # Render world objects with camera
        self.camera.use()
        self.scene.draw()           # Map tiles and platforms
        self.enemies.draw()         # Enemy sprites
        
        # Draw enemy health bars
        for enemy in self.enemies:
            enemy.draw_hp_bar()
        
        # Draw attack/projectile sprites
        self.knight_attacks.draw()
        self.archer_arrows.draw()
        self.wizard_fires.draw()
        
        # Render UI elements without camera (fixed position)
        self.gui_camera.use()
        self.health_bar_list.draw()
        self.draw_instructions()

    def on_update(self, delta_time):
        """
        Main game loop update function. 
        Handles all game logic including:
        - Player movement and abilities
        - Enemy behavior
        - Collision detection
        - Attack systems
        - Level progression
        - Health and damage systems
        """
        # Update player abilities (dash, float, invincibility timers)
        self.player.update_abilities(delta_time)
        
        # Make camera follow player
        self.camera.position = self.player.sprite.position
        
        # Check for damage from hazards
        if arcade.check_for_collision_with_list(
            self.player.sprite, self.danger):
            self.player.take_damage()
            self.update_health_display()
        
        # Handle climbing mechanics
        touching_climbable = self.player.is_touching_climbable_wall(
        self.climbable_walls)
        if self.player.update_movement():
            return  # Early return if special movement is active
            
        # Adjust physics for climbing (disable gravity when climbing)
        if (self.player.is_climbing and touching_climbable and
        self.player.sprite == self.player.knight_sprite):
            self.physics_engine.gravity_constant = 0
        else:
            self.player.is_climbing = False
            self.physics_engine.gravity_constant = GRAVITY
            self.physics_engine.update()
            
        # Check for falling off the map
        if self.player.sprite.center_y <= self.map_bottom: 
            self.player.reset()
            
        # Update player animations
        self.player.update_animations(delta_time, self.player.is_climbing,
        touching_climbable, self.climbable_walls)

        # Update all game entities
        self.enemies.update(delta_time)
        self.knight_attacks.update(delta_time)
        self.archer_arrows.update()
        self.wizard_fires.update(delta_time)
        
        # Handle level progression (levels 1-2 have exits, 
        # level 3 requires killing all enemies)
        if self.level < 3 and arcade.check_for_collision_with_list(
        self.player.sprite, self.exits):
            self.switch_to_next_level()
        
        # Clean up arrows that hit walls or go off-screen
        for arrow in self.archer_arrows:
            # Calculate camera bounds for cleanup
            camera_left = self.camera.position.x - WINDOW_WIDTH // 2
            camera_right = self.camera.position.x + WINDOW_WIDTH // 2
            camera_bottom = self.camera.position.y - WINDOW_HEIGHT // 2
            camera_top = self.camera.position.y + WINDOW_HEIGHT // 2
            
            # Remove arrow if it hits a wall or goes too far off-screen
            if (arcade.check_for_collision_with_list(
            arrow, self.scene["Platforms"]) or
                arrow.center_x < camera_left - 200 or
                arrow.center_x > camera_right + 200 or
                arrow.center_y < camera_bottom - 200 or
                arrow.center_y > camera_top + 200):
                arrow.remove_from_sprite_lists()
        
        # Handle attack collision with enemies
        enemies_to_remove = []
        
        # Knight attacks (high damage, short range)
        for attack in self.knight_attacks:
            hit_enemies = arcade.check_for_collision_with_list(
            attack, self.enemies)
            for enemy in hit_enemies:
                if enemy.take_damage(3):  # Knight does 3 damage
                    enemies_to_remove.append(enemy)
                attack.remove_from_sprite_lists()
                break  # Attack is consumed after hitting one enemy
        
        # Archer arrows (low damage, long range)
        for arrow in self.archer_arrows:
            hit_enemies = arcade.check_for_collision_with_list(
            arrow, self.enemies)
            for enemy in hit_enemies:
                if enemy.take_damage(1):  # Archer does 1 damage
                    enemies_to_remove.append(enemy)
                arrow.remove_from_sprite_lists()
                break  # Arrow is consumed after hitting one enemy
                
        # Wizard fire (medium damage, area effect)
        for fire in self.wizard_fires:
            hit_enemies = arcade.check_for_collision_with_list(
            fire, self.enemies)
            for enemy in hit_enemies:
                if enemy.take_damage(2):  # Wizard does 2 damage
                    enemies_to_remove.append(enemy)
                fire.remove_from_sprite_lists()
                break  # Fire is consumed after hitting one enemy
        
        # Remove defeated enemies from the game
        for enemy in enemies_to_remove:
            enemy.remove_from_sprite_lists()
                
        # Handle player collision with enemies (damage player)
        if arcade.check_for_collision_with_list(
        self.player.sprite, self.enemies):
            if not self.player.is_invincible:
                self.player.take_damage()
                self.update_health_display()
        
        # Handle checkpoint system (heal player and set new spawn point)
        if self.checkpoints:
            hit_checkpoints = arcade.check_for_collision_with_list(
            self.player.sprite, self.checkpoints)
            if hit_checkpoints: 
                # Restore full health at checkpoint
                self.player.health = self.player.max_health
                self.update_health_display()
                
                # Set new spawn points for newly activated checkpoints
                for checkpoint in hit_checkpoints:
                    checkpoint_id = (
                    f"{checkpoint.center_x}_{checkpoint.center_y}")
                    if checkpoint_id not in self.activated_checkpoints:
                        self.activated_checkpoints.add(checkpoint_id)
                        self.player.set_spawn_point(
                        checkpoint.center_x, checkpoint.center_y)
        
        # Check victory condition for level 3
        if self.level == 3 and len(self.enemies) == 0:
            self.game_won = True
            return

    def on_key_press(self, key, modifiers):
        """
        Handle keyboard input for player movement,
        abilities, and game controls.
        """
        # Toggle instruction display
        if key == arcade.key.I:
            self.show_instructions = not self.show_instructions
            return
            
        touching_climbable = self.player.is_touching_climbable_wall(
        self.climbable_walls)
        
        # Reset player position to spawn point
        if key == arcade.key.ESCAPE:
            self.player.reset()
            
        # Character switching 
        # (only when not floating to prevent mid-air switching)
        if not self.player.is_floating:  
            if key == arcade.key.KEY_1:
                self.switch_player_sprite(0)  # Switch to archer
            elif key == arcade.key.KEY_2:
                self.switch_player_sprite(1)  # Switch to knight
            elif key == arcade.key.KEY_3:
                self.switch_player_sprite(2)  # Switch to wizard
                
        # Jumping and climbing
        if key in [arcade.key.UP, arcade.key.W]:
            if self.physics_engine.can_jump():
                self.player.sprite.change_y = PLAYER_JUMP_SPEED
            elif self.player.is_climbing:
                # Jump off climbable wall
                self.player.is_climbing = False
                self.player.sprite.change_y = PLAYER_JUMP_SPEED
                
        # Stop climbing when pressing down
        if key in [arcade.key.DOWN]:
            if touching_climbable:
                self.player.is_climbing = False
                
        # Horizontal movement
        if key in [arcade.key.LEFT, arcade.key.A]:
            self.player.sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key in [arcade.key.RIGHT, arcade.key.D]:
            self.player.sprite.change_x = PLAYER_MOVEMENT_SPEED
            
        # Character-specific abilities (Space key)
        if key in [arcade.key.SPACE]:
            touching_climbable = self.player.is_touching_climbable_wall(
            self.climbable_walls)
            
            # Knight climbing ability
            if touching_climbable:
                self.player.is_climbing = True
                self.player.sprite.change_y = PLAYER_MOVEMENT_SPEED
                # Set climbing animation
                climb_textures = self.player.walk_textures_by_character.get(
                "knight", {}).get("climb", [])
                if climb_textures and len(climb_textures) > 0:
                    self.player.climb_animation_index = 0
                    self.player.sprite.texture = climb_textures[0]
                    
            # Archer dash ability
            elif (self.player.sprite == self.player.archer_sprite 
            and not self.player.archer_dashing):
                if not self.player.archer_dash_on_cd:
                    self.player.start_archer_dash()
                    
            # Wizard float ability (only when on ground)
            elif (self.player.sprite == self.player.wizard_sprite and
            self.physics_engine.can_jump()):
                self.player.start_wizard_float()
                
        # Attack command
        if key in [arcade.key.E]:
            attack = self.player.perform_attack()
            if attack:
                # Add attack to appropriate sprite
                # list based on character
                character_name = self.player.sprite.character_name
                if character_name == "knight":
                    self.knight_attacks.append(attack)
                elif character_name == "archer":
                    self.archer_arrows.append(attack)
                elif character_name == "wizard":
                    self.wizard_fires.append(attack)
                    
    def on_key_release(self, key, modifiers):
        """
        Handle keyboard key release events.
        """
        # Stop horizontal movement when releasing movement keys
        if key in [arcade.key.LEFT,
        arcade.key.A, arcade.key.RIGHT, arcade.key.D]:
            self.player.sprite.change_x = 0
            
        # Stop vertical climbing movement when
        # releasing space while climbing
        if key in [arcade.key.SPACE] and self.player.is_climbing:
            self.player.sprite.change_y = 0
            
    def switch_player_sprite(self, target_index):
        """
        Switch between different character sprites 
        (archer, knight, wizard).
        Preserves position, velocity, and properly
        updates physics engine.
        (0=archer, 1=knight, 2=wizard)
        """
        # Validate input and prevent switching to current character
        if (target_index == self.player.current_character_index or 
            not (0 <= target_index < len(self.player.character_sprites))):
            return
            
        # Remove current sprite from scene
        self.scene["Player"].remove(self.player.sprite)
        
        # Store current state to preserve across character switch
        x = self.player.sprite.center_x
        y = self.player.sprite.bottom
        change_x = self.player.sprite.change_x
        change_y = self.player.sprite.change_y
        
        # Switch to new character
        self.player.current_character_index = target_index
        self.player.sprite = self.player.character_sprites[target_index]
        
        # Restore position and velocity
        self.player.sprite.center_x = x
        self.player.sprite.bottom = y
        self.player.sprite.change_x = change_x
        self.player.sprite.change_y = change_y
        
        # Set appropriate starting texture for new character
        name = self.player.sprite.character_name
        if (
        name in self.player.walk_textures_by_character
        and self.player.walk_textures_by_character[name]["right"]):
            self.player.sprite.texture = ( 
            self.player.walk_textures_by_character
            [name][self.player.facing_direction][0])
        
        # Reset animation and state variables
        self.player.walk_animation_index = 0
        self.player.climb_animation_index = 0
        self.player.movement_accumulator = 0
        self.player.climb_movement_accumulator = 0
        self.player.is_attacking = False
        self.player.attack_timer = 0
        
        # Add new sprite to scene and update physics engine
        self.scene.add_sprite("Player", self.player.sprite)
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player.sprite, walls=self.scene["Platforms"],
        gravity_constant=GRAVITY)

def main():
    """
    Main entry point for the game. 
    Creates the game window and starts the game loop.
    """
    window = GameView()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()