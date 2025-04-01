start run.bat
timeout /t 10
start python airsim_keyboard_controller.py
start python airsim_target_detection.py
@REM start python airsim_texture_replacement.py
start python airsim_get_position.py
start python airsim_gunshot_detection.py