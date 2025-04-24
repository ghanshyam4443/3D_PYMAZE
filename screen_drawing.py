"""
Contains functions for performing most display related tasks, including
drawing columns, sprites, and HUD elements. Most audio and texture
loading/selection is handled in resources.py rather than here.
"""
import math
import random
from typing import Dict, List, Optional, Tuple, Union

import pygame

import maze_levels
import net_data
from config_loader import Config
from level import Level
from maze_game import TEXTURE_WIDTH, TEXTURE_HEIGHT, EmptySound

WHITE = (0xFF, 0xFF, 0xFF)
BLACK = (0x00, 0x00, 0x00)
BLUE = (0x00, 0x30, 0xFF)
LIGHT_BLUE = (0x07, 0xF0, 0xF0)
GOLD = (0xE1, 0xBB, 0x12)
DARK_GOLD = (0x70, 0x5E, 0x09)
GREEN = (0x00, 0xFF, 0x10)
DARK_GREEN = (0x00, 0x80, 0x00)
RED = (0xFF, 0x00, 0x00)
DARK_RED = (0x80, 0x00, 0x00)
PURPLE = (0x87, 0x23, 0xD9)
GREY = (0xAA, 0xAA, 0xAA)
DARK_GREY = (0x20, 0x20, 0x20)
LIGHT_GREY = (0xCD, 0xCD, 0xCD)
WALL_GREY_LIGHT = (0x55, 0x55, 0x55)
WALL_GREY_DARK = (0x33, 0x33, 0x33)

# HUD icons
COMPASS = 0
FLAG = 1
MAP = 2
PAUSE = 3
PLACE_WALL = 4
STATS = 5
KEY_SENSOR = 6
GUN = 7

pygame.font.init()
FONT = pygame.font.SysFont('Tahoma', 24, True)
TITLE_FONT = pygame.font.SysFont('Tahoma', 30, True)

pygame.init()

total_time_on_screen: List[float] = []
victory_sounds_played: List[int] = []


def draw_victory_screen(screen: pygame.Surface, cfg: Config,
                        background: pygame.Surface,
                        highscores: List[Tuple[float, float]],
                        current_level: int, time_score: float,
                        move_score: float, frame_time: float, is_coop: bool,
                        victory_increment: Union[
                            pygame.mixer.Sound, EmptySound
                        ],
                        victory_next_block: Union[
                            pygame.mixer.Sound, EmptySound
                        ], level_json_path: str) -> None:
    """
    Draw the victory screen seen after beating a level. Displays numerous
    scores to the player in a gradual animation.
    """
    level_count = len(maze_levels.load_level_json(level_json_path))
    while len(total_time_on_screen) < level_count:
        total_time_on_screen.append(0.0)
    while len(victory_sounds_played) < level_count:
        victory_sounds_played.append(0)
    total_time_on_screen[current_level] += frame_time
    time_on_screen = total_time_on_screen[current_level]
    screen.blit(background, (0, 0))
    victory_background = pygame.Surface(
        (cfg.viewport_width, cfg.viewport_height)
    )
    victory_background.fill(GREEN)
    victory_background.set_alpha(195)
    screen.blit(victory_background, (0, 0))
    time_score_text = FONT.render(
        f"Time Score: {time_score * min(1.0, time_on_screen / 2):.1f}", True,
        DARK_RED
    )
    if time_on_screen < 2 and victory_sounds_played[current_level] == 0:
        victory_sounds_played[current_level] = 1
        victory_increment.play()
    screen.blit(time_score_text, (10, 10))
    if time_on_screen >= 2 and victory_sounds_played[current_level] == 1:
        victory_sounds_played[current_level] = 2
        victory_next_block.play()
    if time_on_screen >= 2.5:
        move_score_text = FONT.render(
            "Move Score: "
            + f"{move_score * min(1.0, (time_on_screen - 2.5) / 2):.1f}",
            True, DARK_RED
        )
        if victory_sounds_played[current_level] == 2:
            victory_sounds_played[current_level] = 3
            victory_increment.play()
        screen.blit(move_score_text, (10, 40))
        if time_on_screen >= 4.5 and victory_sounds_played[current_level] == 3:
            victory_sounds_played[current_level] = 4
            victory_next_block.play()
    if time_on_screen >= 5.5:
        best_time_score_text = FONT.render(
            f"Best Time Score: {highscores[current_level][0]:.1f}", True,
            DARK_RED
        )
        best_move_score_text = FONT.render(
            f"Best Move Score: {highscores[current_level][1]:.1f}", True,
            DARK_RED
        )
        screen.blit(best_time_score_text, (10, 90))
        screen.blit(best_move_score_text, (10, 120))
        if victory_sounds_played[current_level] == 4:
            victory_sounds_played[current_level] = 5
            victory_next_block.play()
    if time_on_screen >= 6.5:
        best_total_time_score_text = FONT.render(
            f"Best Game Time Score: {sum(x[0] for x in highscores):.1f}", True,
            DARK_RED
        )
        best_total_move_score_text = FONT.render(
            f"Best Game Move Score: {sum(x[1] for x in highscores):.1f}", True,
            DARK_RED
        )
        screen.blit(best_total_time_score_text, (10, 200))
        screen.blit(best_total_move_score_text, (10, 230))
        if victory_sounds_played[current_level] == 5:
            victory_sounds_played[current_level] = 6
            victory_next_block.play()
    if (time_on_screen >= 7.5
            and (current_level < level_count - 1 or is_coop)):
        lower_hint_text = FONT.render(
            "Restart the server to play another level"
            if is_coop else "Press `]` to go to next level", True, DARK_RED
        )
        screen.blit(lower_hint_text, (10, 280))
        if victory_sounds_played[current_level] == 6:
            victory_sounds_played[current_level] = 0  # Reset
            victory_next_block.play()


def draw_kill_screen(screen: pygame.Surface, cfg: Config,
                     jumpscare_monster_texture: pygame.Surface,
                     multi: bool, coop: bool) -> None:
    """
    Draw the red kill screen with the monster fullscreen.
    Also used in multiplayer to display the player's killer.
    """
    jumpscare_monster_texture = pygame.transform.scale(
        jumpscare_monster_texture, (cfg.viewport_width, cfg.viewport_height)
    )
    screen.fill(RED)
    screen.blit(jumpscare_monster_texture, (
        0, 0, cfg.viewport_width, cfg.viewport_height
    ))
    if not coop:
        reset_hint = FONT.render(
            "Press any key to respawn"
            if multi else "Press R to reset the level", True, WHITE
        )
        screen.blit(
            reset_hint,
            (
                cfg.viewport_width // 2 - reset_hint.get_width() // 2,
                cfg.viewport_height - 45
            )
        )


def draw_escape_screen(screen: pygame.Surface, cfg: Config,
                       jumpscare_monster_texture: pygame.Surface) -> None:
    """
    Draw the monster fullscreen and prompt the user to spam W to escape.
    """
    jumpscare_monster_texture = pygame.transform.scale(
        jumpscare_monster_texture, (cfg.viewport_width, cfg.viewport_height)
    )
    screen.blit(jumpscare_monster_texture, (
        random.randint(-5, 5), random.randint(-5, 5),
        cfg.viewport_width, cfg.viewport_height
    ))
    background = pygame.Surface((cfg.viewport_width, 55))
    background.fill(BLACK)
    background.set_alpha(127)
    screen.blit(background, (0, cfg.viewport_height - 55))
    escape_prompt = FONT.render(
        "Press W as fast as you can to escape!", True, WHITE
    )
    screen.blit(
        escape_prompt,
        (
            cfg.viewport_width // 2 - escape_prompt.get_width() // 2,
            cfg.viewport_height - 45
        )
    )


def draw_untextured_column(screen: pygame.Surface, cfg: Config, index: int,
                           side_was_ns: bool, column_height: int) -> None:
    """
    Draw a single black/grey column to the screen. Designed for if textures
    are disabled or a texture wasn't found for the current level.
    """
    display_column_width = cfg.viewport_width // cfg.display_columns
    column_height = min(column_height, cfg.viewport_height)
    colour = WALL_GREY_LIGHT if side_was_ns else WALL_GREY_DARK
    # The location on the screen to start drawing the column
    draw_x = display_column_width * index
    draw_y = max(0, -column_height // 2 + cfg.viewport_height // 2)
    pygame.draw.rect(
        screen, colour, (draw_x, draw_y, display_column_width, column_height)
    )
    if cfg.fog_strength > 0:
        fog_overlay = pygame.Surface(
            (display_column_width, min(column_height, cfg.viewport_height))
        )
        fog_overlay.fill(BLACK)
        fog_overlay.set_alpha(round(
            255 / (column_height / cfg.viewport_height * cfg.fog_strength)
        ))
        screen.blit(fog_overlay, (draw_x, draw_y))


def draw_textured_column(screen: pygame.Surface, cfg: Config,
                         coord: Tuple[float, float], side_was_ns: bool,
                         column_height: int, index: int,
                         facing: Tuple[float, float], texture: pygame.Surface,
                         camera_plane: Tuple[float, float]
                         ) -> None:
    """
    Takes a single column of pixels from the given texture and scales it to
    the required height before drawing it to the screen.
    """
    # Determines how far along the texture we need to go by keeping only the
    # decimal part of the collision coordinate.
    display_column_width = cfg.viewport_width // cfg.display_columns
    position_along_wall = coord[int(not side_was_ns)] % 1
    texture_x = (position_along_wall * TEXTURE_WIDTH).__trunc__()
    camera_x = 2 * index / cfg.display_columns - 1
    cast_direction = (
        facing[0] + camera_plane[0] * camera_x,
        facing[1] + camera_plane[1] * camera_x,
    )
    if not side_was_ns and cast_direction[0] < 0:
        texture_x = TEXTURE_WIDTH - texture_x - 1
    elif side_was_ns and cast_direction[1] > 0:
        texture_x = TEXTURE_WIDTH - texture_x - 1
    # The location on the screen to start drawing the column
    draw_x = display_column_width * index
    draw_y = max(0, -column_height // 2 + cfg.viewport_height // 2)
    # Get a single column of pixels
    pixel_column = texture.subsurface(texture_x, 0, 1, TEXTURE_HEIGHT)
    if (column_height > cfg.viewport_height
            and column_height > cfg.texture_scale_limit):
        # Crop the column so we are only scaling pixels that will be within the
        # viewport. This will boost performance, at the cost of making textures
        # uneven. This will only occur if the column is taller than the config
        # value in texture_scale_limit.
        overlap = (
            (column_height - cfg.viewport_height)
            / ((column_height - TEXTURE_HEIGHT) / TEXTURE_HEIGHT)
        ).__trunc__()
        pixel_column = pixel_column.subsurface(
            0, overlap // 2, 1, TEXTURE_HEIGHT - overlap
        )
    # Scale the pixel column to fill required height
    pixel_column = pygame.transform.scale(
        pixel_column,
        (
            display_column_width,
            min(column_height, cfg.viewport_height)
            if column_height > cfg.texture_scale_limit else
            column_height
        )
    )
    # Ensure capped height pixel columns still render in the correct Y
    # position.
    if cfg.viewport_height < column_height <= cfg.texture_scale_limit:
        overlap = (column_height - cfg.viewport_height) // 2
        pixel_column = pixel_column.subsurface(
            0, overlap, display_column_width, cfg.viewport_height
        )
    screen.blit(pixel_column, (draw_x, draw_y))
    if cfg.draw_reflections:
        pixel_column = pygame.transform.flip(
            pixel_column, False, True
        ).convert_alpha()
        pixel_column.fill(
            (255, 255, 255, 25), special_flags=pygame.BLEND_RGBA_MULT
        )
        screen.blit(pixel_column, (draw_x, draw_y + column_height))
    if cfg.fog_strength > 0:
        fog_overlay = pygame.Surface((
            display_column_width, min(
                (column_height * 2)
                if cfg.draw_reflections else column_height,
                cfg.viewport_height
            )
        ))
        fog_overlay.fill(BLACK)
        fog_overlay.set_alpha(round(
            255 / (column_height / cfg.viewport_height * cfg.fog_strength)
        ))
        screen.blit(fog_overlay, (draw_x, draw_y))


def draw_sprite(screen: pygame.Surface, cfg: Config,
                coord: Tuple[float, float], player_coords: Tuple[float, float],
                camera_plane: Tuple[float, float], facing: Tuple[float, float],
                texture: pygame.Surface) -> None:
    """
    Draw a transformed 2D sprite onto the screen. Provides the illusion of
    an object being drawn in 3D space by scaling up and down.
    """
    display_column_width = cfg.viewport_width // cfg.display_columns
    filled_screen_width = display_column_width * cfg.display_columns
    relative_pos = (coord[0] - player_coords[0], coord[1] - player_coords[1])
    inverse_camera = (
        1 / (camera_plane[0] * facing[1] - facing[0] * camera_plane[1])
    )
    transformation = (
        inverse_camera * (
            facing[1] * relative_pos[0] - facing[0] * relative_pos[1]
        ),
        inverse_camera * (
            -camera_plane[1] * relative_pos[0] + camera_plane[0]
            * relative_pos[1]
        )
    )
    # Prevent divisions by 0
    if transformation[1] == 0:
        return
    screen_x_pos = (
        (filled_screen_width / 2) * (1 + transformation[0] / transformation[1])
    ).__trunc__()
    if (screen_x_pos > filled_screen_width + TEXTURE_WIDTH // 2
            or screen_x_pos < -TEXTURE_WIDTH // 2):
        # Sprite is fully off screen - don't render it
        return
    sprite_size = (
        filled_screen_width // transformation[1],
        cfg.viewport_height // transformation[1]
    )
    if sprite_size[0] <= 0 or sprite_size[1] <= 0:
        # Sprite is behind player - don't render it
        return
    if (sprite_size[0] > cfg.sprite_scale_limit
            or sprite_size[1] > cfg.sprite_scale_limit):
        return
    scaled_texture = pygame.transform.scale(texture, sprite_size)
    if cfg.fog_strength > 0:
        fog_overlay = pygame.Surface(sprite_size)
        fog_overlay.fill(
            # Ensure value between 0 and 255
            (max(round(255 - (255 / (
                sprite_size[1] / cfg.viewport_height * cfg.fog_strength
            ))), 0),) * 3
        )
        scaled_texture.blit(
            fog_overlay, (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT
            # Multiply sprite pixel values by values in overlay
        )
    screen.blit(
        scaled_texture, (
            screen_x_pos - sprite_size[0] // 2,
            cfg.viewport_height // 2 - sprite_size[1] // 2
        )
    )
    if cfg.draw_reflections:
        scaled_texture = pygame.transform.flip(scaled_texture, False, True)
        scaled_texture.fill(
            (255, 255, 255, 25), special_flags=pygame.BLEND_RGBA_MULT
        )
        screen.blit(
            scaled_texture, (
                screen_x_pos - sprite_size[0] // 2,
                cfg.viewport_height // 2 + sprite_size[1] // 2
            )
        )


def draw_solid_background(screen: pygame.Surface, cfg: Config) -> None:
    """
    Draw two rectangles stacked on top of each other horizontally on the
    screen.
    """
    display_column_width = cfg.viewport_width // cfg.display_columns
    filled_screen_width = display_column_width * cfg.display_columns
    # Draw solid sky
    pygame.draw.rect(
        screen, BLUE, (0, 0, filled_screen_width, cfg.viewport_height // 2)
    )
    # Draw solid floor
    pygame.draw.rect(
        screen, DARK_GREY,
        (
            0, cfg.viewport_height // 2, filled_screen_width,
            cfg.viewport_height // 2
        )
    )


def draw_sky_texture(screen: pygame.Surface, cfg: Config,
                     facing: Tuple[float, float],
                     camera_plane: Tuple[float, float],
                     sky_texture: pygame.Surface) -> None:
    """
    Draw textured sky based on facing direction. Player position does not
    affect sky, only direction.
    """
    display_column_width = cfg.viewport_width // cfg.display_columns
    for index in range(cfg.display_columns):
        camera_x = 2 * index / cfg.display_columns - 1
        cast_direction = (
            facing[0] + camera_plane[0] * camera_x,
            facing[1] + camera_plane[1] * camera_x,
        )
        angle = math.atan2(*cast_direction)
        texture_x = math.floor(angle / math.pi * TEXTURE_WIDTH)
        # Creates a "mirror" effect preventing a seam when the texture repeats.
        texture_x = (
            texture_x % TEXTURE_WIDTH
            if angle >= 0 else
            TEXTURE_WIDTH - (texture_x % TEXTURE_WIDTH) - 1
        )
        # Get a single column of pixels
        scaled_pixel_column = pygame.transform.scale(
            sky_texture.subsurface(texture_x, 0, 1, TEXTURE_HEIGHT),
            (display_column_width, cfg.viewport_height // 2)
        )
        screen.blit(scaled_pixel_column, (index * display_column_width, 0))
        if cfg.draw_reflections:
            scaled_pixel_column = pygame.transform.flip(
                scaled_pixel_column, False, True
            )
            scaled_pixel_column.fill(
                (255, 255, 255, 25), special_flags=pygame.BLEND_RGBA_MULT
            )
            screen.blit(
                scaled_pixel_column,
                (index * display_column_width, cfg.viewport_height // 2)
            )


def draw_map(screen: pygame.Surface, cfg: Config, current_level: Level,
             display_rays: bool, ray_end_coords: List[Tuple[float, float]],
             facing: Tuple[float, float], has_key_sensor: bool,
             player_wall: Optional[Tuple[int, int]]) -> None:
    """
    Draw a 2D map representing the current level. This will cover the screen
    unless enable_cheat_map is True in the config.
    """
    tile_width = cfg.viewport_width // current_level.dimensions[0]
    tile_height = cfg.viewport_height // current_level.dimensions[1]
    x_offset = cfg.viewport_width if cfg.enable_cheat_map else 0
    for y, row in enumerate(current_level.wall_map):
        for x, point in enumerate(row):
            if current_level.player_grid_coords == (x, y):
                colour = BLUE
            elif (current_level.monster_coords == (x, y)
                    and cfg.enable_cheat_map):
                colour = DARK_RED
            elif player_wall is not None and player_wall == (x, y):
                colour = PURPLE
            elif (x, y) in current_level.exit_keys and (
                    cfg.enable_cheat_map or has_key_sensor):
                colour = GOLD
            elif (x, y) in current_level.key_sensors and cfg.enable_cheat_map:
                colour = DARK_GOLD
            elif (x, y) in current_level.guns and cfg.enable_cheat_map:
                colour = GREY
            elif current_level.monster_start == (x, y):
                colour = DARK_GREEN
            elif (x, y) in current_level.player_flags:
                colour = LIGHT_BLUE
            elif current_level.start_point == (x, y):
                colour = RED
            elif current_level.end_point == (x, y) and cfg.enable_cheat_map:
                colour = GREEN
            else:
                colour = BLACK if point is not None else WHITE
            pygame.draw.rect(
                screen, colour, (
                    tile_width * x + x_offset,
                    tile_height * y, tile_width, tile_height
                )
            )
    # Raycast rays
    if display_rays and cfg.enable_cheat_map:
        for ray_end in ray_end_coords:
            pygame.draw.line(
                screen, DARK_GOLD, (
                    current_level.player_coords[0]
                    * tile_width + x_offset,
                    current_level.player_coords[1]
                    * tile_height
                ),
                (
                    ray_end[0] * tile_width + x_offset,
                    ray_end[1] * tile_height
                ), 1
            )
    # Player direction
    pygame.draw.line(
        screen, DARK_RED, (
            current_level.player_coords[0] * tile_width + x_offset,
            current_level.player_coords[1] * tile_height
        ),
        (
            current_level.player_coords[0] * tile_width + x_offset + facing[0]
            * min(tile_width, tile_height) // 2,
            current_level.player_coords[1] * tile_height + facing[1]
            * min(tile_width, tile_height) // 2
        ), 3
    )
    # Exact player position
    pygame.draw.circle(
        screen, DARK_GREEN, (
            current_level.player_coords[0] * tile_width + x_offset,
            current_level.player_coords[1] * tile_height
        ), min(tile_width, tile_height) / 8
    )


def draw_stats(screen: pygame.Surface, cfg: Config, monster_spawned: bool,
               time_score: float, move_score: float, remaining_keys: int,
               starting_keys: int, hud_icons: Dict[int, pygame.Surface],
               blank_icon: pygame.Surface, key_sensor_time: float,
               compass_time: float, compass_burned: bool,
               player_wall_time: Optional[float], wall_place_cooldown: float,
               current_level_time: float, has_gun: bool, is_coop: bool
               ) -> None:
    """
    Draw a time, move count, and key counts to the bottom left-hand corner of
    the screen with a transparent black background if the monster hasn't
    spawned or a transparent red one if it has. Also draw some control prompts
    to the top left showing timeouts for wall placement, compass and sensor.
    """
    bottom_background = pygame.Surface((225, 110))
    bottom_background.fill(DARK_RED if monster_spawned else BLACK)
    bottom_background.set_alpha(127)
    screen.blit(bottom_background, (0, cfg.viewport_height - 110))

    time_score_text = FONT.render(f"Time: {time_score:.1f}", True, WHITE)
    move_score_text = FONT.render(f"Moves: {move_score:.1f}", True, WHITE)
    keys_text = FONT.render(
        f"Keys: {remaining_keys}/{starting_keys}", True, WHITE
    )
    screen.blit(time_score_text, (10, cfg.viewport_height - 100))
    screen.blit(move_score_text, (10, cfg.viewport_height - 70))
    screen.blit(keys_text, (10, cfg.viewport_height - 40))

    top_background = pygame.Surface((130 if is_coop else 260, 75))
    top_background.fill(BLACK)
    top_background.set_alpha(127)
    screen.blit(top_background, (0, 0))

    screen.blit(hud_icons.get(MAP, blank_icon), (5, 5))
    screen.blit(FONT.render("‿", True, WHITE), (11, 36))
    top_margin = round(32 * (1 - key_sensor_time / cfg.key_sensor_time))
    cropped_key = hud_icons.get(KEY_SENSOR, blank_icon).subsurface(
        (0, 0, 32, 32 - top_margin)
    )
    screen.blit(cropped_key, (5, 5))

    if not is_coop:
        screen.blit(hud_icons.get(FLAG, blank_icon), (47, 5))
        screen.blit(FONT.render("F", True, WHITE), (54, 40))

        pygame.draw.circle(
            screen, DARK_GREEN if player_wall_time is None else RED, (106, 21),
            round(16 * (
                (1 - wall_place_cooldown / cfg.player_wall_cooldown)
                if player_wall_time is None else
                (
                    1 - (current_level_time - player_wall_time)
                    / cfg.player_wall_time
                )
            ))
        )
        screen.blit(hud_icons.get(PLACE_WALL, blank_icon), (89, 5))
        screen.blit(FONT.render("Q", True, WHITE), (96, 40))

    pygame.draw.circle(
        screen, RED if compass_burned else DARK_GREEN,
        (64 if is_coop else 148, 21),
        round(15 * (compass_time / cfg.compass_time))
    )
    screen.blit(
        hud_icons.get(COMPASS, blank_icon), (47 if is_coop else 131, 5)
    )
    screen.blit(FONT.render("C", True, WHITE), (54 if is_coop else 139, 40))

    if not is_coop:
        screen.blit(hud_icons.get(PAUSE, blank_icon), (173, 5))
        screen.blit(FONT.render("R", True, WHITE), (181, 40))

    screen.blit(hud_icons.get(STATS, blank_icon), (89 if is_coop else 215, 5))
    screen.blit(FONT.render("E", True, WHITE), (96 if is_coop else 223, 40))

    if has_gun:
        gun_background = pygame.Surface((45, 75))
        gun_background.fill(BLACK)
        gun_background.set_alpha(127)
        screen.blit(gun_background, (cfg.viewport_width - 45, 0))
        screen.blit(
            hud_icons.get(GUN, blank_icon), (cfg.viewport_width - 37, 5)
        )
        screen.blit(
            FONT.render("T", True, WHITE), (cfg.viewport_width - 29, 40)
        )


def draw_compass(screen: pygame.Surface, cfg: Config,
                 target: Optional[Tuple[float, float]],
                 source: Tuple[float, float], facing: Tuple[float, float],
                 burned: bool, time_active: float) -> None:
    """
    Draws a compass to the lower right-hand corner of the screen. Points to
    the target from the facing direction of the source, unless it is burned
    or there is no target. The length of the line is determined by how long
    the compass has been active.
    """
    compass_outer_radius = cfg.viewport_width // 6
    compass_inner_radius = compass_outer_radius - cfg.viewport_width // 100
    compass_centre = (
        cfg.viewport_width - compass_outer_radius - cfg.viewport_width // 50,
        cfg.viewport_height - compass_outer_radius - cfg.viewport_width // 50
    )
    pygame.draw.circle(screen, GREY, compass_centre, compass_outer_radius)
    pygame.draw.circle(screen, DARK_GREY, compass_centre, compass_inner_radius)
    if target is not None and not burned:
        # The distance between the player and the monster in each axis.
        relative_pos = (source[0] - target[0], source[1] - target[1])
        # The angle to the monster relative to the facing direction.
        direction = math.atan2(*relative_pos) - math.atan2(*facing)
        # Compass line gets shorter as it runs out of charge.
        line_length = compass_inner_radius * time_active / cfg.compass_time
        line_end_coords = (
            (
                line_length * math.sin(direction) + compass_centre[0]
            ).__trunc__(),
            (
                line_length * math.cos(direction) + compass_centre[1]
            ).__trunc__()
        )
        pygame.draw.line(
            screen, RED, compass_centre, line_end_coords,
            # Cannot be any thinner than 1px
            max(1, cfg.viewport_width // 100)
        )
    elif burned:
        pygame.draw.circle(
            screen, RED, compass_centre, compass_inner_radius
            * (cfg.compass_time - time_active) / cfg.compass_time
        )


def flash_viewport(screen: pygame.Surface, cfg: Config,
                   color: Tuple[int, int, int], strength: float) -> None:
    """
    Draw a transparent overlay over the entire viewport. The strength should be
    a float between 0.0 and 1.0.
    """
    viewport_overlay = pygame.Surface(
        (cfg.viewport_width, cfg.viewport_height)
    )
    viewport_overlay.fill(color)
    viewport_overlay.set_alpha(round(255 * strength))
    screen.blit(viewport_overlay, (0, 0))


def draw_reset_prompt(screen: pygame.Surface, cfg: Config,
                      background: pygame.Surface) -> None:
    """
    Draw a transparent overlay over a given background asking the user if they
    are sure that they want to reset the level.
    """
    screen.blit(background, (0, 0))
    prompt_background = pygame.Surface(
        (cfg.viewport_width, cfg.viewport_height)
    )
    prompt_background.fill(LIGHT_BLUE)
    prompt_background.set_alpha(195)
    screen.blit(prompt_background, (0, 0))
    confirm_text = FONT.render(
        "Press 'y' to reset or 'n' to cancel", True, DARK_GREY
    )
    screen.blit(confirm_text, (
            cfg.viewport_width // 2 - confirm_text.get_width() // 2,
            cfg.viewport_height // 2 - confirm_text.get_height() // 2,
        )
    )


def draw_gun(screen: pygame.Surface, cfg: Config, gun_texture: pygame.Surface
             ) -> None:
    """
    Draw the third person gun on the screen with a crosshair in the centre.
    """
    gun_texture = pygame.transform.scale(
        gun_texture, (cfg.viewport_width, cfg.viewport_height)
    )
    screen.blit(gun_texture, (0, 0, cfg.viewport_width, cfg.viewport_height))
    pygame.draw.circle(
        screen, BLACK, (cfg.viewport_width // 2, cfg.viewport_height // 2), 5
    )
    pygame.draw.circle(
        screen, WHITE, (cfg.viewport_width // 2, cfg.viewport_height // 2), 3
    )


def draw_remaining_hits(screen: pygame.Surface, cfg: Config, hits: int
                        ) -> None:
    """
    Draw the number of hits the player can take before they die in the bottom
    left corner.
    """
    remaining_text = FONT.render(str(hits), True, RED)
    screen.blit(remaining_text, (10, cfg.viewport_height - 40))


def draw_kill_count(screen: pygame.Surface, cfg: Config, kills: int) -> None:
    """
    Draw the number of kills the player has in the bottom right corner.
    """
    kills_text = FONT.render(str(kills), True, GREEN)
    screen.blit(
        kills_text, (
            cfg.viewport_width - kills_text.get_width() - 15,
            cfg.viewport_height - 40
        )
    )


def draw_death_count(screen: pygame.Surface, cfg: Config, deaths: int) -> None:
    """
    Draw the number of deaths the player has in the bottom left corner.
    """
    deaths_text = FONT.render(str(deaths), True, RED)
    screen.blit(deaths_text, (10, cfg.viewport_height - 90))


def draw_leaderboard(screen: pygame.Surface, cfg: Config,
                     players: List[net_data.Player]) -> None:
    """
    Draw an ordered list of players in the server, and the kills and deaths
    they currently have.
    """
    sorted_players = sorted(
        players, key=lambda x: x.kills - x.deaths, reverse=True
    )
    viewport_overlay = pygame.Surface(
        (cfg.viewport_width, cfg.viewport_height)
    )
    viewport_overlay.fill(GREEN)
    viewport_overlay.set_alpha(180)
    screen.blit(viewport_overlay, (0, 0))
    leaderboard_title_text = TITLE_FONT.render("Leaderboard", True, BLUE)
    screen.blit(
        leaderboard_title_text, (
            cfg.viewport_width // 2 - leaderboard_title_text.get_width() // 2,
            10
        )
    )
    header_kills = FONT.render("K", True, BLUE)
    header_deaths = FONT.render("D", True, BLUE)
    header_diff = FONT.render("S", True, BLUE)
    screen.blit(
        header_kills,
        (cfg.viewport_width - 175 - header_kills.get_width() // 2, 55)
    )
    screen.blit(
        header_deaths,
        (cfg.viewport_width - 105 - header_deaths.get_width() // 2, 55)
    )
    screen.blit(
        header_diff,
        (cfg.viewport_width - 35 - header_diff.get_width() // 2, 55)
    )
    for i, plr in enumerate(sorted_players, 1):
        name_text = FONT.render(plr.name, True, BLUE)
        kills_text = FONT.render(str(plr.kills), True, BLUE)
        deaths_text = FONT.render(str(plr.deaths), True, BLUE)
        diff_text = FONT.render(str(plr.kills - plr.deaths), True, BLUE)
        line_y = 33 * i + 65
        screen.blit(name_text, (20, line_y))
        screen.blit(
            kills_text,
            (cfg.viewport_width - 175 - kills_text.get_width() // 2, line_y)
        )
        screen.blit(
            deaths_text,
            (cfg.viewport_width - 105 - deaths_text.get_width() // 2, line_y)
        )
        screen.blit(
            diff_text,
            (cfg.viewport_width - 35 - diff_text.get_width() // 2, line_y)
        )
