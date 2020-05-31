from MainControlLoop.main_control_loop import MainControlLoop

def main():
    mcl = MainControlLoop()
    while True:
        mcl.execute()


if __name__ == '__main__':
    main()