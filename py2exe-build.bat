@echo off
rmdir /q /s dist
c:\python27\python.exe py2exe-setup.py

chdir dist
copy RoguePy\libtcod\*.dll .
mkdir libtcod
copy RoguePy\libtcod\* libtcod
rmdir /q /s build .git
del /q .gitignore
pirates
cd ..