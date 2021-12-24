You must be in the root directory of the project to run the tests.
Use command 
```
sudo apt-get install -y qemu-kvm
sudo usermod $USER -G docker,kvm -a
python3 -m  virtualenv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest .
```
