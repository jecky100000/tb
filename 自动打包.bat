::ɾ�������ļ���
rd /s /q C:\Users\Administrator\tb\__pycache__
rd /s /q C:\Users\Administrator\tb\build\AutoRunTB
pause
::ɾ�������ļ�������Ŀ¼�ļ�
del /f/s/q C:\Users\Administrator\tb\dist\AutoRunTB.exe
del /f/s/q "C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\AutoRunTB.exe"
pause
::���exe�󿽱�������Ŀ¼��
pyinstaller -F -i C:\Users\Administrator\tb\qihuo.ico C:\Users\Administrator\tb\AutoRunTB.py
copy "C:\Users\Administrator\tb\dist\AutoRunTB.exe" "C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\"
pause
::��������
shutdown -r -f -t 0
