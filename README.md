# pfs

## TODO
- [ ] Before deployment: make it so that critical parameters can't be changed in-flight
- [x] Update clock from GPS once/minute
- [ ] Implement bursted telemetry
- [x] Implement commands
- [x] Implement telemetry
- [x] Implement deferred function running
- [ ] Implement automatic process restarting
- [ ] Sanity checks
- [?] spec
- [ ] **Documentation** - almost done
- [ ] EPS watchdog petting
- [ ] Initial deployment (submodule?)

## Dependencies
* If running on a local development environment, run `pip3 install -r requirements.txt` to install the dependencies.
* `smbus`/`smbus2` are not compatible with Windows cmd, either:
    * Use Linux/WSL to install and run
    * Run remotely on `pi-cubesat` with `ssh`

## Development
Use `pipenv` to manage the development environment.
More information on `pipenv` available in the [documentation](https://pipenv.readthedocs.io/en/latest/).
If you already have `pipenv` installed, run:
```
pipenv install  # Install depedencies
pipenv run python3 main.py  # Run the flight software
```
Alternatively, configure your IDE to use the pipenv as the Python interpreter.