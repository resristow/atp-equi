import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {'include_files':['../ajuda.py'], 'includes':['argparse']}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = 'Console'
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "ATP-equi",
        version = "1.0",
        description = "Automatic building of ATP /branch card from conversion of .ana file equivalents",
        options = {"build_exe": build_exe_options},
        executables = [Executable("../atp-py.py", base=base)])