import logging

logger = logging.getLogger("CI")

total_received: int = 0
total_errors: int = 0
total_success: int = 0

# All currently registered commands.  The key is the function identifier in the air, and values follow
# the format {"function": func, "args": args}  where args is an array of types (e.g. int, str, float, etc.)
registered_commands = {}


# Annotation to register a function as a command
# Example usage:
# @command("aprs_set_bperiod", int)
# def set_bperiod(period: int) -> str:
# ...

def command(command_name, *args, **kwargs):
    """
    Given a function name, return a decorator that registers that function.
    :return: Decorator that registers function.
    """
    def decorator(func):
        registered_commands[command_name] = {"function": func, "args": args}
        return func

    return decorator


def generate_checksum(body: str):
    """
    Given a message body, generate its checksum
    :param body: The body of the message.
    :return: Generated checksum for the message.
    """
    global sum1
    sum1 = sum([ord(x) for x in body[0:-7]])
    sum1 %= 26
    sum1 += 65
    logger.debug('CHECKOUT :' + chr(sum1) + ";")
    return chr(sum1)


def dispatch(body: str) -> None:
    """
    Given a raw radio packet, verify its checksum and execute it if it's a command.
    Both radios will call this function whenever they receive an incoming message.
    :param body: The body of a raw radio packet.
    :return: None
    """
    global total_errors, total_received, total_success
    if body[0:2] == 'TJ' and body[-5:-1] == '\\r\\n':  # TODO: exception proof this (index out of bounds)
        if generate_checksum(body) == body[-7]:  # TODO: exception proof (index out of bounds)
            logger.debug("Message %s passed checksum." % body)
            total_received += 1
            # Parse and execute command.
            cmd = body[2:].strip().split(",")
            if cmd[0] not in registered_commands:
                logger.warning("Command with correct checksum not registered.")
                return
            if len(registered_commands[cmd[0]]["args"]) != len(cmd) - 1:
                logger.warning("Incorrect number of arguments for command.")
                total_errors += 1
                return
            args = []
            for i, argtype in enumerate(registered_commands[cmd[0]]["args"]):
                try:
                    if argtype == str:  # Don't call str() on a string, as that puts extra quotes around it
                        args.append(cmd[i + 1])
                    else:
                        args.append(argtype(cmd[i + 1]))
                except:
                    # There was an error when converting an argument
                    logger.debug("Unable to parse argument for command.")
                    total_errors += 1
                    return
            try:
                # Actually execute the command
                resp = registered_commands[cmd[0]]["function"](*args)
                if resp is not None:
                    # TODO: Enqueue as an event message
                    pass
            except Exception as e:
                logger.error("Exception when executing command %s: %s" % (cmd[0], str(e)))
                total_errors += 1
                return
            total_success += 1
    else:
        # The message was not intended for us.
        # logger.debug('Invalid message')
        pass

# def start():
#     global modules, m_aprs, m_gps, m_adcs, m_eps
#     # modules = {'A':core,'B':m_aprs,'C':'iridium','D':'housekeeping','E':'log','F':'GPS'}
#     m_aprs = {'a': aprs.enqueue, 'b': aprs.enter_normal_mode, 'c': aprs.enter_low_power_mode,
#               'd': aprs.enter_emergency_mode}
#     m_gps = {'a': gps.sendgpsthruaprs, 'b': gps.queryfield, 'c': gps.querygps, 'd': gps.querypastgps,
#              'e': gps.getsinglegps, 'f': gps.enter_normal_mode, 'g': gps.enter_low_power_mode,
#              'h': gps.enter_emergency_mode}
#     # m_adcs = {'a': adcs.enter_normal_mode, 'b': adcs.enter_low_power_mode, 'c': adcs.enter_emergency_mode}
#     # m_eps = {'a': eps.pin_on, 'b': eps.pin_off, 'c': eps.get_PDM_status, 'd': eps.get_board_status, 'e': eps.set_system_watchdog_timeout, 'f': eps.get_BCR1_volts, 'g': eps.get_BCR1_amps_A, 'h': eps.get_BCR1_amps_B, 'i': eps.get_board_telem, 'j': eps.enter_normal_mode, 'k': eps.enter_low_power_mode, 'l': eps.enter_emergency_mode}
#     # m_imu = {'a': imu.enter_normal_mode, 'b': imu.enter_low_power_mode, 'c': imu.enter_emergency_mode}
#     # m_iridium = {}  # BLANK - nothing useful is in iridium.py
#     # m_housekeeping = {'a': housekeeping.enter_normal_mode, 'b': housekeeping.enter_low_power_mode, 'c': housekeeping.enter_emergency_mode}
#     # m_telemetry = {'a': telemetry.gps_subpacket, 'b': telemetry.adcs_subpacket, 'c': telemetry.comms_subpacket, 'd': telemetry.system_subpacket}
#     modules = {'B': m_aprs, 'F': m_gps}
#     # modules = {'B': m_aprs, 'C': m_iridium, 'D': m_housekeeping, 'F': m_gps, 'G': m_eps, 'H': m_adcs, 'I': m_imu, 'J': m_telemetry}
#     # core = {}
