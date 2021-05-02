py -m build

if %errorlevel% neq 0 exit /b %errorlevel%

twine upload --config-file .pypirc dist/*
