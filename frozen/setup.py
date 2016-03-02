import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {'include_files':['../ajuda.py'], 'includes':['argparse','win32api','win32com.client']}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = 'Console'
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "ATP-equi",
        version = "1.1",
        description = "Automatic building of ATP /BRANCH card from conversion of .ANA file equivalents",
        options = {"build_exe": build_exe_options},
        executables = [Executable("../atp-equi.py", base=base, icon='icone.bmp', compress=1)])
        # executables = [Executable("../atp-py.py", base=base)])