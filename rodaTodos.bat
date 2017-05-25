echo off
setlocal EnableDelayedExpansion
SET GNUDIR=c:\atp\atpmingw\
SET DIREXE=c:\atp\tpbigs
set arq[0]=RMONO_ARE52_JSU52_
set arq[1]=ENERG_ARE52_JSU52_
set arq[2]=ENERG_ARE52_JSU52_1F
set arq[3]=RELIG_ARE52_JSU52_CS
set arq[4]=RELIG_ARE52_JSU52_SS
for /L %%i in (0,1,4) do (
    %DIREXE%\mytpbig_leo.exe disk !arq[%%i]!.atp s -r > !arq[%%i]!.log 2>&1
    MD !arq[%%i]!
    MOVE SHOT*.DAT .\!arq[%%i]!
    MOVE !arq[%%i]!.* .\!arq[%%i]!
    )

DEL *.BIN
DEL *.BAK
DEL *.46
DEL *.6
REM shutdown -s now