# pfs

## TODO
- [ ] Before deployment: make it so that critical parameters can't be changed in-flight
- [x] Update clock from GPS once/minute
- [ ] Implement bursted telemetry
- [x] Implement commands
- [x] Implement telemetry
- [x] Implement deferred function running
- [x] Implement automatic process restarting
- [x] Make Iridium stable and usable
- [ ] Sanity checks
- [ ] **Documentation** - almost done
- [ ] EPS watchdog petting
- [ ] Initial deployment (submodule?)


## Development

Use `pipenv` to manage the development environment.
More information on `pipenv` available in the [documentation](https://pipenv.readthedocs.io/en/latest/).
If you already have `pipenv` installed, run:
```
pipenv install  # Install dependencies
```
Alternatively, configure your IDE to use the pipenv as the Python interpreter.

## Usage

`invoke` is used as the task runner.
Ensure that you install `invoke` globally (not in your virtual environment) using `pip3 install invoke`.
Below are the available commands:

- `invoke run`: Run the flight software.
    - `invoke run -d`: Debug mode.
    - `invoke run -p`: Production mode, use this when running on a staging or production environment.
- `invoke deploy`: Install all required packages _globally_. Only run this on a staging or production environment.


## Dependencies
* `smbus`/`smbus2` are not compatible with Windows `cmd.exe`, either:
    * Use Linux/WSL to install and run
    * Run remotely on `pi-cubesat` with `ssh`