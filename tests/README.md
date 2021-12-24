You must be in the root directory of the project to run the tests.
Use command 
```
sudo usermod $USER -g docker -a
python3 -m  virtualenv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest .
```
