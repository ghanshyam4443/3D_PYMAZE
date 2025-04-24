"""
Contains most of the resources used by the game, including textures and sound effects.
"""
import os
from glob import glob
from typing import Any, Dict, List, Tuple, Union

import pygame

import raycasting
import screen_drawing
from maze_game import TEXTURE_WIDTH, TEXTURE_HEIGHT, EmptySound

# Change working directory to the directory where the script is located.
os.chdir(os.path.dirname(__file__))

# Prevent discard variable from triggering type checkers
_: Any

# Texture and sound caches
texture_cache: Dict[str, pygame.Surface] = {}
sound_cache: Dict[str, Union[pygame.mixer.Sound, EmptySound]] = {}

def load_texture(texture_path: str, use_alpha: bool = False) -> pygame.Surface:
    """Load a texture from a file and cache it for reuse."""
    if texture_path in texture_cache:
        return texture_cache[texture_path]
    try:
        texture = (
            pygame.image.load(texture_path).convert_alpha()
            if use_alpha
            else pygame.image.load(texture_path).convert()
        )
        texture_cache[texture_path] = texture
        print(f"Loaded texture: {texture_path}")  # Debugging
        return texture
    except FileNotFoundError:
        print(f"Texture not found: {texture_path}")
        fallback = pygame.Surface((TEXTURE_WIDTH, TEXTURE_HEIGHT))
        texture_cache[texture_path] = fallback
        return fallback

def reload_texture(texture_path: str, use_alpha: bool = False) -> pygame.Surface:
    """Force reload a texture, updating the cache."""
    try:
        texture = (
            pygame.image.load(texture_path).convert_alpha()
            if use_alpha
            else pygame.image.load(texture_path).convert()
        )
        texture_cache[texture_path] = texture
        print(f"Reloaded texture: {texture_path}")  # Debugging
        return texture
    except FileNotFoundError:
        print(f"Texture not found: {texture_path}")
        fallback = pygame.Surface((TEXTURE_WIDTH, TEXTURE_HEIGHT))
        texture_cache[texture_path] = fallback
        return fallback

def load_sound(sound_path: str) -> Union[pygame.mixer.Sound, EmptySound]:
    """Load a sound from a file and cache it for reuse."""
    if sound_path in sound_cache:
        return sound_cache[sound_path]
    try:
        sound = pygame.mixer.Sound(sound_path)
        sound_cache[sound_path] = sound
        return sound
    except (FileNotFoundError, pygame.error):
        print(f"Sound not found or failed to load: {sound_path}")
        empty_sound = EmptySound()
        sound_cache[sound_path] = empty_sound
        return empty_sound

# Load placeholder texture
placeholder_texture = load_texture(os.path.join("textures", "placeholder.png"), use_alpha=True)

# Used to create the darker versions of each texture
_darkener = pygame.Surface((TEXTURE_WIDTH, TEXTURE_HEIGHT))
_darkener.fill(screen_drawing.BLACK)
_darkener.set_alpha(127)

# Load wall textures
wall_textures: Dict[str, Tuple[pygame.Surface, pygame.Surface]] = {}
for texture_file in glob(os.path.join("textures", "wall", "*.png")):
    texture_name = os.path.split(texture_file)[-1].split(".")[0]
    light_texture = load_texture(texture_file)
    dark_texture = light_texture.copy()
    dark_texture.blit(_darkener, (0, 0))
    wall_textures[texture_name] = (light_texture, dark_texture)

# Add placeholder wall texture
wall_textures["placeholder"] = (placeholder_texture, placeholder_texture.copy())

# Load decoration textures
decoration_textures: Dict[str, pygame.Surface] = {
    os.path.split(x)[-1].split(".")[0]: load_texture(x, use_alpha=True)
    for x in glob(os.path.join("textures", "sprite", "decoration", "*.png"))
}
decoration_textures["placeholder"] = placeholder_texture

# Load player textures
player_textures: List[pygame.Surface] = [
    load_texture(x, use_alpha=True)
    for x in glob(os.path.join("textures", "sprite", "player", "*.png"))
]

# Load player wall textures
player_wall_textures: Dict[int, Tuple[pygame.Surface, pygame.Surface]] = {}
for texture_file in glob(os.path.join("textures", "player_wall", "*.png")):
    degradation_stage = int(os.path.split(texture_file)[-1].split(".")[0])
    light_texture = load_texture(texture_file)
    dark_texture = light_texture.copy()
    dark_texture.blit(_darkener, (0, 0))
    player_wall_textures[degradation_stage] = (light_texture, dark_texture)

if not player_wall_textures:
    player_wall_textures[0] = (placeholder_texture, placeholder_texture.copy())

# Load sky texture
sky_texture = load_texture(os.path.join("textures", "sky.png"), use_alpha=True)

# Load sprite textures
sprite_textures = {
    getattr(raycasting, os.path.split(x)[-1].split(".")[0].upper()): load_texture(x, use_alpha=True)
    for x in glob(os.path.join("textures", "sprite", "*.png"))
}

# Load HUD icons
blank_icon = pygame.Surface((32, 32))
hud_icons = {
    getattr(screen_drawing, os.path.split(x)[-1].split(".")[0].upper()): pygame.transform.scale(load_texture(x, use_alpha=True), (32, 32))
    for x in glob(os.path.join('textures', 'hud_icons', '*.png'))
}

# Load first-person gun texture
first_person_gun = pygame.transform.scale(
    load_texture(os.path.join('textures', 'gun_fp.png'), use_alpha=True),
    (TEXTURE_WIDTH, TEXTURE_HEIGHT)
)

# Load jumpscare monster texture
monster_texture_path = os.path.join("textures", "death_monster.png")
jumpscare_monster_texture = pygame.transform.scale(
    reload_texture(monster_texture_path, use_alpha=True),  # Force reload
    (TEXTURE_WIDTH, TEXTURE_HEIGHT)
)
print(f"Monster texture dimensions: {jumpscare_monster_texture.get_size()}")  # Debugging

# Load sounds
audio_error_occurred = False
try:
    monster_jumpscare_sound = load_sound(os.path.join("sounds", "monster_jumpscare.wav"))
    monster_spotted_sound = load_sound(os.path.join("sounds", "monster_spotted.wav"))
    breathing_sounds = {
        0: load_sound(os.path.join("sounds", "player_breathe", "heavy.wav")),
        5: load_sound(os.path.join("sounds", "player_breathe", "medium.wav")),
        10: load_sound(os.path.join("sounds", "player_breathe", "light.wav"))
    }
    footstep_sounds = [load_sound(x) for x in glob(os.path.join("sounds", "footsteps", "*.wav"))]
    monster_roam_sounds = [load_sound(x) for x in glob(os.path.join("sounds", "monster_roam", "*.wav"))]
    key_pickup_sounds = [load_sound(x) for x in glob(os.path.join("sounds", "key_pickup", "*.wav"))]
    key_sensor_pickup_sound = load_sound(os.path.join("sounds", "sensor_pickup.wav"))
    gun_pickup_sound = load_sound(os.path.join("sounds", "gun_pickup.wav"))
    flag_place_sounds = [load_sound(x) for x in glob(os.path.join("sounds", "flag_place", "*.wav"))]
    wall_place_sounds = [load_sound(x) for x in glob(os.path.join("sounds", "wall_place", "*.wav"))]
    compass_open_sound = load_sound(os.path.join("sounds", "compass_open.wav"))
    compass_close_sound = load_sound(os.path.join("sounds", "compass_close.wav"))
    map_open_sound = load_sound(os.path.join("sounds", "map_open.wav"))
    map_close_sound = load_sound(os.path.join("sounds", "map_close.wav"))
    gunshot_sound = load_sound(os.path.join("sounds", "gunshot.wav"))
    pygame.mixer.music.load(os.path.join("sounds", "ambience.wav"))
    light_flicker_sound = load_sound(os.path.join("sounds", "light_flicker.wav"))
    player_hit_sound = load_sound(os.path.join("sounds", "player_hit.wav"))
    victory_increment = load_sound(os.path.join("sounds", "victory_increment.wav"))
    victory_next_block = load_sound(os.path.join("sounds", "victory_next_block.wav"))
except Exception as e:
    audio_error_occurred = True
    print(f"Audio loading error: {e}")