@echo off
 
echo . 
echo ...initing
 
set str_time_first_bit="%time:~0,1%"
if %str_time_first_bit%==" " (
	set str_date_time=%date:~0,4%%date:~5,2%%date:~8,2%_0%time:~1,1%%time:~3,2%%time:~6,2%
)else ( 
	set str_date_time=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
)

::md ../../output/%str_date_time%
pyinstaller -D -w scripts/main.py ^
            --name th10s ^
            --clean ^
            --distpath ./output/%str_date_time% ^
            --icon=./source/qrc/inste.ico ^
            --workpath=./build
pause
exit