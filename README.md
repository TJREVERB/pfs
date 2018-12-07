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
