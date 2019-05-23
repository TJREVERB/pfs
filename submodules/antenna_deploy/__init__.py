import isisants

def start():
    # Initiate connection with the device
    isisants.py_k_ants_init(b"/dev/i2c-1", 0x31, 0x32, 4, 10)

    # Arms the device
    isisants.py_k_ants_arm()
    

    # Run the deploy methods
    ANT_1 = 0
    ANT_2 = 1
    ANT_3 = 2
    ANT_4 = 3
    isisants.py_k_ants_deploy(ANT_1, False, 5)
    isisants.py_k_ants_deploy(ANT_2, False, 5)
    isisants.py_k_ants_deploy(ANT_3, False, 5)
    isisants.py_k_ants_deploy(ANT_4, False, 5)
