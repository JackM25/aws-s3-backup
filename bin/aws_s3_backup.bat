@echo off
SET startDir=%cd%
cd %~dp0..
pipenv run main.py %*
cd %startDir%