import PyInstaller.__main__

# Define the name of your main script
script_name = "main.py"

PyInstaller.__main__.run(
    [
        script_name,
        "--onefile",  # Pack everything into a single .exe
        "--windowed",  # Prevent a command prompt from opening
        "--name=CAN_Pro_Decoder",  # The name of your executable
        "--clean",  # Clean cache before building
        "--hidden-import=cantools",  # Ensure cantools is bundled
        "--icon=app_icon.ico",  # THIS adds the icon to the .exe
        "--add-data=app_icon.ico;.",  # This bundles the icon INSIDE the exe
    ]
)

print("\nBuild complete! Check the 'dist' folder for your executable.")
