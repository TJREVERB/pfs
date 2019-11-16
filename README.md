# pFS
## Python Flight Software

## Development
1. Clone this repo
2. Use `venv` to manage the development environment.
3. Create a new `virtualenv`
```
$ python3 -m venv venv
```
4. Activate the `virtualenv`
```
$ source venv/bin/activate
```
5. Install dependencies from requirements.txt
```
$ pip install -r requirements.txt
```
6. Run pFS
```
$ python main.py
```
Alternatively, you can set `main.py` as executable and run `main.py as a script
```
$ chmod +x main.py # only do this once
$ ./main.py
```

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