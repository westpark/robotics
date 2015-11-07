if "%~1"=="" (set controller=remote) ELSE (set controller=%1)
if "%~2"=="" (set robot=text) ELSE (set robot=%1)
py -3 -mpiwars.controllers --controller=%controller% --robot=%robot%

