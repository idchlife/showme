echo "Building..."
pipenv run pyinstaller --onefile cli.py -p $(pipenv --venv)"/lib/python3.7/site-packages" --add-data "app/web/templates:app/web/templates" --add-data "app/web/assets:app/web/assets"