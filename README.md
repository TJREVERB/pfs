# pFS
## Python Flight Software

## Development
1. Clone this repo
2. Use `pipenv` to manage the development environment.
More information on `pipenv` available in the [documentation](https://pipenv.readthedocs.io/en/latest/).
If you already have `pipenv` installed, run:
```
pipenv install  # Install dependencies
```
* Alternatively, configure your IDE to use the pipenv as the Python interpreter.
3. Activate the `pipenv shell`
4. Run `python3 main.py`

## Dependencies
- `Python 3.6` or greater is required along with `pip`
### Usage
`invoke` is used as the task runner.
Ensure that you install `invoke` globally (not in your virtual environment) using `pip3 install invoke`.
Below are the available commands:

- `invoke run`: Run the flight software.
    - `invoke run -d`: Debug mode.
    - `invoke run -p`: Production mode, use this when running on a staging or production environment.
- `invoke deploy`: Install all required packages _globally_. Only run this on a staging or production environment.