# Let's start with some default (for me) imports...

from cx_Freeze import setup, Executable

# Process the includes, excludes and packages first

includes = []
excludes = []
packages = ['paramiko']
path = []

GUI2Exe_Target_1 = Executable(
    # what to build
    script = "parking_info.py",
    initScript = None,
    base = 'Win32GUI',
    targetDir = r"dist",
    targetName = "parking.exe",
    )

setup(

    version = "1.0",
    description = "No Description",
    author = "No Author",
    name = "Parking info",

    options = {"build_exe": {"includes": includes,
                 "excludes": excludes,
                 "packages": packages,
                 "path": path
                 }
           },

    executables = [GUI2Exe_Target_1]
    )