# -*- mode: python -*-

block_cipher = None


a = Analysis(['..\\atp-equi.py'],
             pathex=['D:\\Ferramentas\\Projeto ATP_Py\\atp-equi\\releases'],
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
          name='atp-equi-1.0.1-x86.exe',
          debug=False,
          strip=False,
          upx=True,
          console=True )
