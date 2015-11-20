if "%~1"=="" (set shell=text) ELSE (set shell=%1)
py -3 -mpiwars.shells --shell=%shell%
PAUSE