# -*- mode: python -*-

block_cipher = None


a = Analysis(['..\\atp-equi.py'],
             pathex=['D:\\Ferramentas\\atp-equi\\releases'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='atp-equi-x64.exe',
          debug=False,
          strip=False,
          upx=True,
          console=True )
