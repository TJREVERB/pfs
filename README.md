# pfs

## TODO
- [x] Update clock from GPS once/minute
- [ ] Implement bursted telemetry
- [x] Implement commands
- [x] Implement telemetry
- [ ] Implement automatic process restarting
- [ ] sanity checks
- [?] spec
- [ ] **documentation**
- [ ] EPS watchdog petting
- [ ] Inital deployment (submodule?)

## Dependencies
* If running on a local development environment, run ```pip3 install -r requirements.txt``` to install the dependencies.
* `smbus`/`smbus2` are not compatible with Windows cmd, either:
    * Use Linux/WSL to install and run
    * Run remotely on `pi-cubesat` with `ssh`
