import importlib
from core import config


def main():
    print("Config:")
    print(config)
    print()
    # Load all the modules
    for module in config['modules']:
        pass


if __name__ == '__main__':
    main()
