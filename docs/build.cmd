CALL make.bat html
IF ERRORLEVEL 1 GOTO error
start _build\html\index.html
PAUSE
GOTO xit

:error
PAUSE
GOTO xit

:xit

