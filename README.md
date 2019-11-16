# pFS
## Python Flight Software

### This branch is used for testing purposes only
### UNDER _NO_ CIRCUMSTANCE IS THIS BRANCH TO BE MERGED INTO `master`

#### Process
1. Clone this repo
2. Checkout onto `testing`
```
$ git checkout testing
```
3. Update from `master`
```
$ git pull origin master
```
4. For unit testing, add unit test files in the respective submodules' directory
  * e.g. Unit Test for telemetry
  ```
  submodules/
    telemetry/
      __init__.py 
      test.py # create this file
  ```
5. Each unit test file should have a `run_tests` method which basically runs all unit test cases
6. `submodules/tests.py` will automatically scrape each submodule for a `test.py` file and call `run_tests` on that file if present
7. Record any errors and submit them as Issues on this repository

#### Testing Framework
* Each submodule directory should have a `test.py` file.
  * EXCEPTION: Radios
    * test files for Radios
      * `submodules/radios/aprs_test.py`
      * `submodules/radios/iridium_test.py`
  * Everything else:
    * `submodules/[submodule]/test.py`
* `submodules/tests.py` shall attempt to import `test.py` for all submodules and will try to run the `run_tests` function in each submodule that it successfully imported
* A submodule's `test.py` should create a new instance of its target submodule's class along with any dependencies it requires. A submodule's `test.py` should also create a fake `config` variable to mimic `config_*.yml`

#### Reporting Bugs
1. Record the submodule, test case, input, actual output, and expected output
2. Record the exact process of how the bug was discovered
3. Include any information that can possibily aid in debugging
4. Create a new Issue, with the testers and developers as assignees. Also keep the programming lead informed of this process