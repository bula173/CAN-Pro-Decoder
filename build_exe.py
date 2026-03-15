import platform
from pathlib import Path

import PyInstaller.__main__

# Detect platform
is_windows = platform.system() == "Windows"
separator = ";" if is_windows else ":"

# Define the name of your main script
script_name = "main.py"

# Build arguments
args = [
    script_name,
    "--onefile",  # Pack everything into a single .exe
    "--windowed",  # Prevent a command prompt from opening
    "--name=CAN_Pro_Decoder",  # The name of your executable
    "--clean",  # Clean cache before building
    "--hidden-import=cantools",  # Ensure cantools is bundled
    "-y",  # Overwrite output without asking
]

# Only add icon if it exists
icon_path = Path("app_icon.ico")
if icon_path.exists():
    args.append(f"--icon={icon_path}")
    args.append(f"--add-data=app_icon.ico{separator}.")
else:
    print("Warning: app_icon.ico not found. Building without custom icon.")

print(f"Building for {platform.system()} with separator: '{separator}'")
print(f"PyInstaller arguments: {args}\n")

PyInstaller.__main__.run(args)

print("\n[SUCCESS] Build complete! Check the 'dist' folder for your executable.")
if is_windows:
    print("[OUTPUT] Executable: dist/CAN_Pro_Decoder.exe")
else:
    print("[OUTPUT] Executable: dist/CAN_Pro_Decoder")
