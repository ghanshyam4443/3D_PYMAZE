import configparser
import os
import tkinter
import tkinter.ttk
from typing import Dict, Optional, Tuple
class ConfigEditorApp:
    """
    A tkinter GUI providing a user-friendly way to easily edit the game's
    config file. While the app should still function if the file is erroneous
    or missing, unexpected behaviour may occur.
    """
    def __init__(self, root: tkinter.Tk) -> None:
        # Change working directory to the directory where the script is located
        # This prevents issues with required files not being found.
        os.chdir(os.path.dirname(__file__))

        self.config = configparser.ConfigParser(allow_no_value=True)
        # Preserve the case of option names
        self.config.optionxform = str  # type: ignore
        # Looks for the config.ini file in the script directory regardless of
        # working directory.
        self.config.read("config.ini")
        if 'OPTIONS' not in self.config:
            self.config['OPTIONS'] = {}
        self.config_options = self.config['OPTIONS']

        self.window = tkinter.Toplevel(root)
        self.window.wm_title("PyMaze Config")
        self.window.wm_iconbitmap(
            self, os.path.join("window_icons", "config.ico")
        )

        # Stores the labels above sliders along with their template strings
        # so that their text values can be dynamically changed easily.
        self.scale_labels: Dict[str, Tuple[tkinter.Label, str]] = {}
        # Stores the checkbox variables for each bool field so that their state
        # can be dynamically retrieved easily.
        self.checkbuttons: Dict[str, tkinter.IntVar] = {}

        self.gui_restart_warning_label = tkinter.Label(
            self.window, fg='red',
            text="Be aware that some settings may not work properly or cause "
            + "issues until after restarting the game"
        )
        self.gui_restart_warning_label.pack(fill='x', expand=True)

        self.gui_top_tab_control = tkinter.ttk.Notebook(self.window)
        self.gui_top_tab_control.pack(fill="both", expand=True)

        self.gui_basic_config_frame = tkinter.Frame(self.gui_top_tab_control)
        self.gui_top_tab_control.add(self.gui_basic_config_frame, text="Basic")

        self.gui_advanced_config_frame = tkinter.Frame(
            self.gui_top_tab_control
        )
        self.gui_top_tab_control.add(
            self.gui_advanced_config_frame, text="Advanced"
        )

        self.gui_viewport_width_label = tkinter.Label(
            self.gui_basic_config_frame, anchor=tkinter.W,
            text=f"View Width — ({self.parse_int('VIEWPORT_WIDTH', 500)})"
        )
        self.scale_labels['VIEWPORT_WIDTH'] = (
            self.gui_viewport_width_label, "View Width — ({})"
        )
        self.gui_viewport_width_slider = tkinter.ttk.Scale(
            self.gui_basic_config_frame, from_=500, to=3840,
            value=self.parse_int('VIEWPORT_WIDTH', 500),
            command=lambda x: self.on_scale_change('VIEWPORT_WIDTH', x, 0)
        )
        self.gui_viewport_width_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_viewport_width_slider.pack(fill="x", anchor=tkinter.NW)

        self.gui_viewport_height_label = tkinter.Label(
            self.gui_basic_config_frame, anchor=tkinter.W,
            text=f"View Height — ({self.parse_int('VIEWPORT_HEIGHT', 500)})"
        )
        self.scale_labels['VIEWPORT_HEIGHT'] = (
            self.gui_viewport_height_label, "View Height — ({})"
        )
        self.gui_viewport_height_slider = tkinter.ttk.Scale(
            self.gui_basic_config_frame, from_=500, to=2160,
            value=self.parse_int('VIEWPORT_HEIGHT', 500),
            command=lambda x: self.on_scale_change('VIEWPORT_HEIGHT', x, 0)
        )
        self.gui_viewport_height_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_viewport_height_slider.pack(fill="x", anchor=tkinter.NW)

        self.checkbuttons['ENABLE_CHEAT_MAP'] = tkinter.IntVar()
        self.gui_cheat_map_check = tkinter.Checkbutton(
            self.gui_basic_config_frame, anchor=tkinter.W,
            variable=self.checkbuttons['ENABLE_CHEAT_MAP'],
            text="Enable the cheat map"
        )
        if self.parse_bool('ENABLE_CHEAT_MAP', False):
            self.gui_cheat_map_check.select()
        # Set command after select to prevent it from being called
        self.gui_cheat_map_check.config(
            command=lambda: self.on_checkbutton_click('ENABLE_CHEAT_MAP')
        )
        self.gui_cheat_map_check.pack(fill="x", anchor=tkinter.NW)

        self.checkbuttons['MONSTER_ENABLED'] = tkinter.IntVar()
        self.gui_monster_check = tkinter.Checkbutton(
            self.gui_basic_config_frame, anchor=tkinter.W,
            variable=self.checkbuttons['MONSTER_ENABLED'],
            text="Enable the monster"
        )
        if self.parse_bool('MONSTER_ENABLED', True):
            self.gui_monster_check.select()
        # Set command after select to prevent it from being called
        self.gui_monster_check.config(
            command=lambda: self.on_checkbutton_click('MONSTER_ENABLED')
        )
        self.gui_monster_check.pack(fill="x", anchor=tkinter.NW)

        self.checkbuttons['MONSTER_SOUND_ON_KILL'] = tkinter.IntVar()
        self.gui_monster_kill_sound_check = tkinter.Checkbutton(
            self.gui_basic_config_frame, anchor=tkinter.W,
            variable=self.checkbuttons['MONSTER_SOUND_ON_KILL'],
            text="Play the jumpscare sound on death"
        )
        if self.parse_bool('MONSTER_SOUND_ON_KILL', True):
            self.gui_monster_kill_sound_check.select()
        # Set command after select to prevent it from being called
        self.gui_monster_kill_sound_check.config(
            command=lambda: self.on_checkbutton_click('MONSTER_SOUND_ON_KILL')
        )
        self.gui_monster_kill_sound_check.pack(fill="x", anchor=tkinter.NW)

        self.checkbuttons['MONSTER_SOUND_ON_SPOT'] = tkinter.IntVar()
        self.gui_monster_spot_sound_check = tkinter.Checkbutton(
            self.gui_basic_config_frame, anchor=tkinter.W,
            variable=self.checkbuttons['MONSTER_SOUND_ON_SPOT'],
            text="Play a jumpscare sound when the monster is spotted"
        )
        if self.parse_bool('MONSTER_SOUND_ON_SPOT', True):
            self.gui_monster_spot_sound_check.select()
        # Set command after select to prevent it from being called
        self.gui_monster_spot_sound_check.config(
            command=lambda: self.on_checkbutton_click('MONSTER_SOUND_ON_SPOT')
        )
        self.gui_monster_spot_sound_check.pack(fill="x", anchor=tkinter.NW)

        self.checkbuttons['MONSTER_FLICKER_LIGHTS'] = tkinter.IntVar()
        self.gui_monster_flicker_lights_check = tkinter.Checkbutton(
            self.gui_basic_config_frame, anchor=tkinter.W,
            variable=self.checkbuttons['MONSTER_FLICKER_LIGHTS'],
            text="Flicker lights based on distance to the monster"
        )
        if self.parse_bool('MONSTER_FLICKER_LIGHTS', True):
            self.gui_monster_flicker_lights_check.select()
        # Set command after select to prevent it from being called
        self.gui_monster_flicker_lights_check.config(
            command=lambda: self.on_checkbutton_click('MONSTER_FLICKER_LIGHTS')
        )
        self.gui_monster_flicker_lights_check.pack(fill="x", anchor=tkinter.NW)

        self.checkbuttons['MONSTER_SOUND_ROAMING'] = tkinter.IntVar()
        self.gui_monster_sound_roaming_check = tkinter.Checkbutton(
            self.gui_basic_config_frame, anchor=tkinter.W,
            variable=self.checkbuttons['MONSTER_SOUND_ROAMING'],
            text="Play random monster roaming sounds"
        )
        if self.parse_bool('MONSTER_SOUND_ROAMING', True):
            self.gui_monster_sound_roaming_check.select()
        # Set command after select to prevent it from being called
        self.gui_monster_sound_roaming_check.config(
            command=lambda: self.on_checkbutton_click('MONSTER_SOUND_ROAMING')
        )
        self.gui_monster_sound_roaming_check.pack(fill="x", anchor=tkinter.NW)

        self.gui_frame_rate_limit_label = tkinter.Label(
            self.gui_basic_config_frame, anchor=tkinter.W,
            text=f"Max FPS — ({self.parse_int('FRAME_RATE_LIMIT', 75)})"
        )
        self.scale_labels['FRAME_RATE_LIMIT'] = (
            self.gui_frame_rate_limit_label, "Max FPS — ({})"
        )
        self.gui_frame_rate_limit_slider = tkinter.ttk.Scale(
            self.gui_basic_config_frame, from_=8, to=360,
            value=self.parse_int('FRAME_RATE_LIMIT', 75),
            command=lambda x: self.on_scale_change('FRAME_RATE_LIMIT', x, 0)
        )
        self.gui_frame_rate_limit_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_frame_rate_limit_slider.pack(fill="x", anchor=tkinter.NW)

        self.gui_compass_time_label = tkinter.Label(
            self.gui_basic_config_frame, anchor=tkinter.W,
            text="Time before compass burnout (seconds) — "
            + f"({self.parse_float('COMPASS_TIME', 10.0)})"
        )
        self.scale_labels['COMPASS_TIME'] = (
            self.gui_compass_time_label,
            "Time before compass burnout (seconds) — ({})"
        )
        self.gui_compass_time_slider = tkinter.ttk.Scale(
            self.gui_basic_config_frame, from_=1.0, to=60.0,
            value=self.parse_float('COMPASS_TIME', 10.0),
            command=lambda x: self.on_scale_change('COMPASS_TIME', x, 1)
        )
        self.gui_compass_time_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_compass_time_slider.pack(fill="x", anchor=tkinter.NW)

        self.gui_monster_time_to_escape_label = tkinter.Label(
            self.gui_basic_config_frame, anchor=tkinter.W,
            text="Total time to escape monster per level (seconds) — "
                 + f"({self.parse_float('MONSTER_TIME_TO_ESCAPE', 5.0)})"
        )
        self.scale_labels['MONSTER_TIME_TO_ESCAPE'] = (
            self.gui_monster_time_to_escape_label,
            "Total time to escape monster per level (seconds) — ({})"
        )
        self.gui_monster_time_to_escape_slider = tkinter.ttk.Scale(
            self.gui_basic_config_frame, from_=1.0, to=30.0,
            value=self.parse_float('MONSTER_TIME_TO_ESCAPE', 5.0),
            command=lambda x: self.on_scale_change(
                'MONSTER_TIME_TO_ESCAPE', x, 1
            )
        )
        self.gui_monster_time_to_escape_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_monster_time_to_escape_slider.pack(
            fill="x", anchor=tkinter.NW
        )

        self.gui_monster_presses_to_escape_label = tkinter.Label(
            self.gui_basic_config_frame, anchor=tkinter.W,
            text="Total key presses to escape monster — "
                 + f"({self.parse_int('MONSTER_PRESSES_TO_ESCAPE', 10)})"
        )
        self.scale_labels['MONSTER_PRESSES_TO_ESCAPE'] = (
            self.gui_monster_presses_to_escape_label,
            "Total key presses to escape monster — ({})"
        )
        self.gui_monster_presses_to_escape_slider = tkinter.ttk.Scale(
            self.gui_basic_config_frame, from_=0, to=60,
            value=self.parse_int('MONSTER_PRESSES_TO_ESCAPE', 10),
            command=lambda x: self.on_scale_change(
                'MONSTER_PRESSES_TO_ESCAPE', x, 0
            )
        )
        self.gui_monster_presses_to_escape_label.pack(
            fill="x", anchor=tkinter.NW
        )
        self.gui_monster_presses_to_escape_slider.pack(
            fill="x", anchor=tkinter.NW
        )

        self.gui_key_sensor_time_label = tkinter.Label(
            self.gui_basic_config_frame, anchor=tkinter.W,
            text="Time key sensor lasts after pickup (seconds) — "
                 + f"({self.parse_float('KEY_SENSOR_TIME', 10.0)})"
        )
        self.scale_labels['KEY_SENSOR_TIME'] = (
            self.gui_key_sensor_time_label,
            "Time key sensor lasts after pickup (seconds) — ({})"
        )
        self.gui_key_sensor_time_slider = tkinter.ttk.Scale(
            self.gui_basic_config_frame, from_=1.0, to=60.0,
            value=self.parse_float('KEY_SENSOR_TIME', 10.0),
            command=lambda x: self.on_scale_change('KEY_SENSOR_TIME', x, 1)
        )
        self.gui_key_sensor_time_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_key_sensor_time_slider.pack(fill="x", anchor=tkinter.NW)

        self.gui_player_wall_time_label = tkinter.Label(
            self.gui_basic_config_frame, anchor=tkinter.W,
            text="Amount of time before player placed walls break (seconds) — "
                 + f"({self.parse_float('PLAYER_WALL_TIME', 15.0)})"
        )
        self.scale_labels['PLAYER_WALL_TIME'] = (
            self.gui_player_wall_time_label,
            "Amount of time before player placed walls break (seconds) — ({})"
        )
        self.gui_player_wall_time_slider = tkinter.ttk.Scale(
            self.gui_basic_config_frame, from_=1.0, to=120.0,
            value=self.parse_float('PLAYER_WALL_TIME', 15.0),
            command=lambda x: self.on_scale_change(
                'PLAYER_WALL_TIME', x, 1
            )
        )
        self.gui_player_wall_time_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_player_wall_time_slider.pack(fill="x", anchor=tkinter.NW)

        self.gui_player_wall_cooldown_label = tkinter.Label(
            self.gui_basic_config_frame, anchor=tkinter.W,
            text="Cooldown before player can place another wall (seconds) — "
                 + f"({self.parse_float('PLAYER_WALL_COOLDOWN', 20.0)})"
        )
        self.scale_labels['PLAYER_WALL_COOLDOWN'] = (
            self.gui_player_wall_cooldown_label,
            "Cooldown before player can place another wall (seconds) — ({})"
        )
        self.gui_player_wall_cooldown_slider = tkinter.ttk.Scale(
            self.gui_basic_config_frame, from_=0.0, to=120.0,
            value=self.parse_float('PLAYER_WALL_COOLDOWN', 20.0),
            command=lambda x: self.on_scale_change(
                'PLAYER_WALL_COOLDOWN', x, 1
            )
        )
        self.gui_player_wall_cooldown_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_player_wall_cooldown_slider.pack(fill="x", anchor=tkinter.NW)

        self.checkbuttons['TEXTURES_ENABLED'] = tkinter.IntVar()
        self.gui_textures_check = tkinter.Checkbutton(
            self.gui_basic_config_frame, anchor=tkinter.W,
            variable=self.checkbuttons['TEXTURES_ENABLED'],
            text="Display textures on walls (impacts performance heavily)"
        )
        if self.parse_bool('TEXTURES_ENABLED', True):
            self.gui_textures_check.select()
        # Set command after select to prevent it from being called
        self.gui_textures_check.config(
            command=lambda: self.on_checkbutton_click('TEXTURES_ENABLED')
        )
        self.gui_textures_check.pack(fill="x", anchor=tkinter.NW)

        self.checkbuttons['SKY_TEXTURES_ENABLED'] = tkinter.IntVar()
        self.gui_sky_textures_check = tkinter.Checkbutton(
            self.gui_basic_config_frame, anchor=tkinter.W,
            variable=self.checkbuttons['SKY_TEXTURES_ENABLED'],
            text="Display textured sky (impacts performance)"
        )
        if self.parse_bool('SKY_TEXTURES_ENABLED', True):
            self.gui_sky_textures_check.select()
        # Set command after select to prevent it from being called
        self.gui_sky_textures_check.config(
            command=lambda: self.on_checkbutton_click('SKY_TEXTURES_ENABLED')
        )
        self.gui_sky_textures_check.pack(fill="x", anchor=tkinter.NW)

        self.gui_fog_strength_label = tkinter.Label(
            self.gui_basic_config_frame, anchor=tkinter.W,
            text="Fog strength (lower is stronger, 0 is disabled) — "
            + f"({self.parse_float('FOG_STRENGTH', 7.5)})"
        )
        self.scale_labels['FOG_STRENGTH'] = (
            self.gui_fog_strength_label,
            "Fog strength (lower is stronger, 0 is disabled) — ({})"
        )
        self.gui_fog_strength_slider = tkinter.ttk.Scale(
            self.gui_basic_config_frame, from_=0.0, to=20.0,
            value=self.parse_float('FOG_STRENGTH', 7.5),
            command=lambda x: self.on_scale_change('FOG_STRENGTH', x, 1)
        )
        self.gui_fog_strength_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_fog_strength_slider.pack(fill="x", anchor=tkinter.NW)

        self.gui_turn_speed_label = tkinter.Label(
            self.gui_basic_config_frame, anchor=tkinter.W,
            text=f"Turn Sensitivity — ({self.parse_float('TURN_SPEED', 2.5)})"
        )
        self.scale_labels['TURN_SPEED'] = (
            self.gui_turn_speed_label, "Turn Sensitivity — ({})"
        )
        self.gui_turn_speed_slider = tkinter.ttk.Scale(
            self.gui_basic_config_frame, from_=0.1, to=10.0,
            value=self.parse_float('TURN_SPEED', 2.5),
            command=lambda x: self.on_scale_change('TURN_SPEED', x, 2)
        )
        self.gui_turn_speed_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_turn_speed_slider.pack(fill="x", anchor=tkinter.NW)

        display_columns_default = self.parse_int(
            'DISPLAY_COLUMNS', self.parse_int('VIEWPORT_WIDTH', 500)
        )
        self.gui_display_columns_label = tkinter.Label(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            text="Render Resolution (lower this to improve performance) — "
            + f"({display_columns_default})"
        )
        self.scale_labels['DISPLAY_COLUMNS'] = (
            self.gui_display_columns_label,
            "Render Resolution (lower this to improve performance) — ({})"
        )
        self.gui_display_columns_slider = tkinter.ttk.Scale(
            self.gui_advanced_config_frame, from_=24,
            to=self.parse_int('VIEWPORT_WIDTH', 500),
            value=display_columns_default,
            command=lambda x: self.on_scale_change('DISPLAY_COLUMNS', x, 0)
        )
        self.gui_display_columns_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_display_columns_slider.pack(fill="x", anchor=tkinter.NW)

        monster_start_override_value = self.parse_optional_float(
            'MONSTER_START_OVERRIDE', None
        )
        self.gui_monster_start_label = tkinter.Label(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            text="Monster spawn override (seconds) — "
            + f"({self.parse_optional_float('MONSTER_START_OVERRIDE', None)})"
        )
        self.gui_monster_start_info_label = tkinter.Label(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            text="Note: This will not affect levels with no monster", fg="blue"
        )
        self.scale_labels['MONSTER_START_OVERRIDE'] = (
            self.gui_monster_start_label,
            "Monster spawn override (seconds) — ({})"
        )
        self.gui_monster_start_slider = tkinter.ttk.Scale(
            self.gui_advanced_config_frame, from_=-0.1, to=999.9,
            value=(
                monster_start_override_value
                if monster_start_override_value is not None else -0.1
            ),
            command=lambda x: self.on_scale_change(
                'MONSTER_START_OVERRIDE', x, 1
            )
        )
        self.gui_monster_start_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_monster_start_info_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_monster_start_slider.pack(fill="x", anchor=tkinter.NW)

        self.gui_monster_movement_label = tkinter.Label(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            text="Time between monster movements (seconds) — "
            + f"({self.parse_float('MONSTER_MOVEMENT_WAIT', 0.5)})"
        )
        self.gui_monster_movement_warning_label = tkinter.Label(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            text="Warning: This will affect the rate at which lights flicker",
            fg="darkorange"
        )
        self.scale_labels['MONSTER_MOVEMENT_WAIT'] = (
            self.gui_monster_movement_label,
            "Time between monster movements (seconds) — ({})"
        )
        self.gui_monster_movement_slider = tkinter.ttk.Scale(
            self.gui_advanced_config_frame, from_=0.01, to=10.0,
            value=self.parse_float('MONSTER_MOVEMENT_WAIT', 0.5),
            command=lambda x: self.on_scale_change(
                'MONSTER_MOVEMENT_WAIT', x, 2
            )
        )
        self.gui_monster_movement_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_monster_movement_warning_label.pack(
            fill="x", anchor=tkinter.NW
        )
        self.gui_monster_movement_slider.pack(fill="x", anchor=tkinter.NW)

        self.gui_monster_spot_label = tkinter.Label(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            text="Minimum time between spotted jumpscare sounds (seconds) — "
            + f"({self.parse_float('MONSTER_SPOT_TIMEOUT', 10.0)})"
        )
        self.scale_labels['MONSTER_SPOT_TIMEOUT'] = (
            self.gui_monster_spot_label,
            "Minimum time between spotted jumpscare sounds (seconds) — ({})"
        )
        self.gui_monster_spot_slider = tkinter.ttk.Scale(
            self.gui_advanced_config_frame, from_=0.1, to=60.0,
            value=self.parse_float('MONSTER_SPOT_TIMEOUT', 10.0),
            command=lambda x: self.on_scale_change(
                'MONSTER_SPOT_TIMEOUT', x, 1
            )
        )
        self.gui_monster_spot_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_monster_spot_slider.pack(fill="x", anchor=tkinter.NW)

        self.gui_monster_roam_sound_delay_label = tkinter.Label(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            text="Time between monster roaming sounds (seconds) — "
                 + f"({self.parse_float('MONSTER_ROAM_SOUND_DELAY', 7.5)})"
        )
        self.scale_labels['MONSTER_ROAM_SOUND_DELAY'] = (
            self.gui_monster_roam_sound_delay_label,
            "Time between monster roaming sounds (seconds) — ({})"
        )
        self.gui_monster_roam_sound_delay_slider = tkinter.ttk.Scale(
            self.gui_advanced_config_frame, from_=0.1, to=60.0,
            value=self.parse_float('MONSTER_ROAM_SOUND_DELAY', 7.5),
            command=lambda x: self.on_scale_change(
                'MONSTER_ROAM_SOUND_DELAY', x, 1
            )
        )
        self.gui_monster_roam_sound_delay_label.pack(
            fill="x", anchor=tkinter.NW
        )
        self.gui_monster_roam_sound_delay_slider.pack(
            fill="x", anchor=tkinter.NW
        )

        self.gui_compass_norm_charge_label = tkinter.Label(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            text="Normal compass recharge multiplier — "
            + f"({self.parse_float('COMPASS_CHARGE_NORM_MULTIPLIER', 0.5)})"
        )
        self.scale_labels['COMPASS_CHARGE_NORM_MULTIPLIER'] = (
            self.gui_compass_norm_charge_label,
            "Normal compass recharge multiplier — ({})"
        )
        self.gui_compass_norm_charge_slider = tkinter.ttk.Scale(
            self.gui_advanced_config_frame, from_=0.1, to=10.0,
            value=self.parse_float('COMPASS_CHARGE_NORM_MULTIPLIER', 0.5),
            command=lambda x: self.on_scale_change(
                'COMPASS_CHARGE_NORM_MULTIPLIER', x, 1
            )
        )
        self.gui_compass_norm_charge_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_compass_norm_charge_slider.pack(fill="x", anchor=tkinter.NW)

        self.gui_compass_burn_charge_label = tkinter.Label(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            text="Burned compass recharge multiplier — "
            + f"({self.parse_float('COMPASS_CHARGE_BURN_MULTIPLIER', 1.0)})"
        )
        self.scale_labels['COMPASS_CHARGE_BURN_MULTIPLIER'] = (
            self.gui_compass_burn_charge_label,
            "Burned compass recharge multiplier — ({})"
        )
        self.gui_compass_burn_charge_slider = tkinter.ttk.Scale(
            self.gui_advanced_config_frame, from_=0.1, to=10.0,
            value=self.parse_float('COMPASS_CHARGE_BURN_MULTIPLIER', 1.0),
            command=lambda x: self.on_scale_change(
                'COMPASS_CHARGE_BURN_MULTIPLIER', x, 1
            )
        )
        self.gui_compass_burn_charge_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_compass_burn_charge_slider.pack(fill="x", anchor=tkinter.NW)

        self.gui_compass_charge_delay_label = tkinter.Label(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            text="Delay before compass begins recharging (seconds) — "
            + f"({self.parse_float('COMPASS_CHARGE_DELAY', 1.5)})"
        )
        self.scale_labels['COMPASS_CHARGE_DELAY'] = (
            self.gui_compass_charge_delay_label,
            "Delay before compass begins recharging (seconds) — ({})"
        )
        self.gui_compass_charge_delay_slider = tkinter.ttk.Scale(
            self.gui_advanced_config_frame, from_=0.1, to=10.0,
            value=self.parse_float('COMPASS_CHARGE_DELAY', 1.5),
            command=lambda x: self.on_scale_change(
                'COMPASS_CHARGE_DELAY', x, 1
            )
        )
        self.gui_compass_charge_delay_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_compass_charge_delay_slider.pack(fill="x", anchor=tkinter.NW)

        self.gui_texture_scale_label = tkinter.Label(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            text="Internal texture stretch limit — "
            + f"({self.parse_int('TEXTURE_SCALE_LIMIT', 10000)})"
        )
        self.gui_texture_scale_info_label = tkinter.Label(
            self.gui_advanced_config_frame, anchor=tkinter.W, fg="blue",
            text="Note: Lower values will make nearby textures appear jagged"
        )
        self.scale_labels['TEXTURE_SCALE_LIMIT'] = (
            self.gui_texture_scale_label,
            "Internal texture stretch limit — ({})"
        )
        self.gui_texture_scale_slider = tkinter.ttk.Scale(
            self.gui_advanced_config_frame, from_=1, to=100000,
            value=self.parse_int('TEXTURE_SCALE_LIMIT', 10000),
            command=lambda x: self.on_scale_change('TEXTURE_SCALE_LIMIT', x, 0)
        )
        self.gui_texture_scale_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_texture_scale_info_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_texture_scale_slider.pack(fill="x", anchor=tkinter.NW)

        self.gui_display_fov_label = tkinter.Label(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            text=f"Field of View — ({self.parse_int('DISPLAY_FOV', 50)})"
        )
        self.scale_labels['DISPLAY_FOV'] = (
            self.gui_display_fov_label, "Field of View — ({})"
        )
        self.gui_display_fov_slider = tkinter.ttk.Scale(
            self.gui_advanced_config_frame, from_=1, to=100,
            value=self.parse_int('DISPLAY_FOV', 50),
            command=lambda x: self.on_scale_change('DISPLAY_FOV', x, 0)
        )
        self.gui_display_fov_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_display_fov_slider.pack(fill="x", anchor=tkinter.NW)

        self.checkbuttons['DRAW_MAZE_EDGE_AS_WALL'] = tkinter.IntVar()
        self.gui_draw_maze_edge_check = tkinter.Checkbutton(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            variable=self.checkbuttons['DRAW_MAZE_EDGE_AS_WALL'],
            text="Draw the edge of the maze as if it were a wall"
        )
        if self.parse_bool('DRAW_MAZE_EDGE_AS_WALL', True):
            self.gui_draw_maze_edge_check.select()
        # Set command after select to prevent it from being called
        self.gui_draw_maze_edge_check.config(
            command=lambda: self.on_checkbutton_click('DRAW_MAZE_EDGE_AS_WALL')
        )
        self.gui_draw_maze_edge_check.pack(fill="x", anchor=tkinter.NW)

        self.checkbuttons['ENABLE_COLLISION'] = tkinter.IntVar()
        self.gui_enable_collision_check = tkinter.Checkbutton(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            variable=self.checkbuttons['ENABLE_COLLISION'],
            text="Enable wall collision detection"
        )
        if self.parse_bool('ENABLE_COLLISION', True):
            self.gui_enable_collision_check.select()
        # Set command after select to prevent it from being called
        self.gui_enable_collision_check.config(
            command=lambda: self.on_checkbutton_click('ENABLE_COLLISION')
        )
        self.gui_enable_collision_check.pack(fill="x", anchor=tkinter.NW)

        self.checkbuttons['ENABLE_MONSTER_KILLING'] = tkinter.IntVar()
        self.gui_enable_monster_killing_check = tkinter.Checkbutton(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            variable=self.checkbuttons['ENABLE_MONSTER_KILLING'],
            text="Enable monster engagement on collision"
        )
        if self.parse_bool('ENABLE_MONSTER_KILLING', True):
            self.gui_enable_monster_killing_check.select()
        # Set command after select to prevent it from being called
        self.gui_enable_monster_killing_check.config(
            command=lambda: self.on_checkbutton_click('ENABLE_MONSTER_KILLING')
        )
        self.gui_enable_monster_killing_check.pack(fill="x", anchor=tkinter.NW)

        self.checkbuttons['DRAW_REFLECTIONS'] = tkinter.IntVar()
        self.draw_reflections_check = tkinter.Checkbutton(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            variable=self.checkbuttons['DRAW_REFLECTIONS'],
            text="Draw wall and sky reflections on maze floor"
        )
        self.draw_reflections_check_warning_label = tkinter.Label(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            text="Warning: This will have a major negative performance impact",
            fg="darkorange"
        )
        if self.parse_bool('DRAW_REFLECTIONS', True):
            self.draw_reflections_check.select()
        # Set command after select to prevent it from being called
        self.draw_reflections_check.config(
            command=lambda: self.on_checkbutton_click('DRAW_REFLECTIONS')
        )
        self.draw_reflections_check.pack(fill="x", anchor=tkinter.NW)
        self.draw_reflections_check_warning_label.pack(
            fill="x", anchor=tkinter.NW
        )

        self.gui_sprite_scale_label = tkinter.Label(
            self.gui_advanced_config_frame, anchor=tkinter.W,
            text="Sprite scale limit — "
                 + f"({self.parse_int('SPRITE_SCALE_LIMIT', 750)})"
        )
        self.gui_sprite_scale_info_label = tkinter.Label(
            self.gui_advanced_config_frame, anchor=tkinter.W, fg="blue",
            text="Note: Lower values will make closer sprites disappear"
        )
        self.scale_labels['SPRITE_SCALE_LIMIT'] = (
            self.gui_sprite_scale_label,
            "Sprite scale limit — ({})"
        )
        self.gui_sprite_scale_slider = tkinter.ttk.Scale(
            self.gui_advanced_config_frame, from_=1, to=10000,
            value=self.parse_int('SPRITE_SCALE_LIMIT', 750),
            command=lambda x: self.on_scale_change('SPRITE_SCALE_LIMIT', x, 0)
        )
        self.gui_sprite_scale_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_sprite_scale_info_label.pack(fill="x", anchor=tkinter.NW)
        self.gui_sprite_scale_slider.pack(fill="x", anchor=tkinter.NW)

        self.gui_save_button = tkinter.ttk.Button(
            self.window, command=self.save_config, text="Save"
        )
        self.gui_save_button.pack()

        self.window.wait_window()

    def on_scale_change(self, field: str, new_value: str, decimal_places: int
                        ) -> None:
        """
        To be called when the user moves a slider. New_value will always be a
        floating point value represented as a str because of how Tkinter Scales
        work, which will be truncated to the provided number of decimal places.
        Field is the name of the ini field to change. If new_value is negative,
        an empty string will be stored in the ini field instead to represent
        None.
        """
        if field == "VIEWPORT_WIDTH":
            new_width = int(new_value.split(".")[0])
            # Display columns must always be less than or equal to view width.
            self.gui_display_columns_slider.config(to=new_width)
            if (int(self.gui_display_columns_slider.get())
                    >= self.parse_int('VIEWPORT_WIDTH', 500)):
                self.gui_display_columns_slider.set(new_width)  # type: ignore
        # Truncate the number of decimal places on a float represented as a
        # string. If the float is negative, it will be converted to an empty
        # string to represent None.
        to_store = (
            new_value.split(".")[0] + "."
            + new_value.split(".")[1][:decimal_places]
        ).strip('.') if not new_value.startswith('-') else ''
        # INI files can only contain strings
        self.config_options[field] = to_store
        self.scale_labels[field][0].config(
            text=self.scale_labels[field][1].format(
                to_store if to_store != '' else 'None'
            )
        )

    def on_checkbutton_click(self, field: str) -> None:
        """
        To be called when the user checks or unchecks a checkbutton. Toggles
        the boolean value current in the specified field.
        """
        # INI files can only contain strings
        self.config_options[field] = str(self.checkbuttons[field].get())

    def save_config(self) -> None:
        """
        Save the potentially modified configuration options to config.ini
        """
        with open("config.ini", 'w', encoding="utf8") as file:
            self.config.write(file)

    def parse_int(self, field_name: str, default_value: int) -> int:
        """
        Get a value from the configuration with the specified field name as an
        integer. If the value is missing or invalid, default_value will be
        returned.
        """
        if field_name not in self.config_options:
            return default_value
        field = self.config_options[field_name]
        if not field.isnumeric():
            return default_value
        return int(field)

    def parse_float(self, field_name: str, default_value: float) -> float:
        """
        Get a value from the configuration with the specified field name as a
        float. If the value is missing or invalid, default_value will be
        returned.
        """
        if field_name not in self.config_options:
            return default_value
        field = self.config_options[field_name]
        if not field.replace(".", "", 1).isnumeric():
            return default_value
        return float(field)

    def parse_optional_float(self, field_name: str,
                             default_value: Optional[float]
                             ) -> Optional[float]:
        """
        Get a value from the configuration with the specified field name as a
        float or None. If the value is missing or invalid, default_value will
        be returned.
        """
        if field_name not in self.config_options:
            return default_value
        field = self.config_options[field_name]
        if field == '':
            return None
        if not field.replace(".", "", 1).isnumeric():
            return default_value
        return float(field)

    def parse_bool(self, field_name: str, default_value: bool) -> bool:
        """
        Get a value from the configuration with the specified field name as a
        bool. If the value is missing or invalid, default_value will be
        returned.
        """
        if field_name not in self.config_options:
            return default_value
        field = self.config_options[field_name]
        if not field.isnumeric():
            return default_value
        return bool(int(field))


if __name__ == "__main__":
    _root = tkinter.Tk()
    _root.withdraw()
    ConfigEditorApp(_root)
