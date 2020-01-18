from libc.stdint cimport uint8_t, uint16_t, uint32_t
from libcpp cimport bool
cdef extern from "i2c.h":
    ctypedef enum KI2CStatus:
        I2C_OK = 0,
        I2C_ERROR,
        I2C_ERROR_AF,
        I2C_ERROR_ADDR_TIMEOUT,
        I2C_ERROR_TIMEOUT,
        I2C_ERROR_NACK,
        I2C_ERROR_TXE_TIMEOUT,
        I2C_ERROR_BTF_TIMEOUT,
        I2C_ERROR_NULL_HANDLE,
        I2C_ERROR_CONFIG
    KI2CStatus k_i2c_init(char * device, int * fp)
    void k_i2c_terminate(int * fp)
    KI2CStatus k_i2c_write(int i2c, uint16_t addr, uint8_t *ptr, int len)
    KI2CStatus k_i2c_read(int i2c, uint16_t addr, uint8_t *ptr, int len)
cdef extern from "ants-api.h":
    ctypedef enum KANTSAnt:
        ANT_1 =0, 
        ANT_2 =1, 
        ANT_3 =2, 
        ANT_4 =3
    ctypedef struct ants_telemetry:
        uint16_t raw_temp; 
        uint16_t deploy_status;
        uint32_t uptime
    ctypedef enum KANTSStatus:
        ANTS_OK =0, 
        ANTS_ERROR, 
        ANTS_ERROR_CONFIG, 
        ANTS_ERROR_NOT_IMPLEMENTED
    ctypedef enum KANTSController:
        PRIMARY,
        SECONDARY
    KANTSStatus k_ants_init(char * bus, uint8_t primary, uint8_t secondary, uint8_t ant_count, uint32_t timeout)
    void k_ants_terminate()
    KANTSStatus k_ants_configure(KANTSController config)
    KANTSStatus k_ants_reset()
    KANTSStatus k_ants_arm()
    KANTSStatus k_ants_disarm()
    KANTSStatus k_ants_deploy(KANTSAnt antenna, bool override, uint8_t timeout)
    KANTSStatus k_ants_auto_deploy(uint8_t timeout)
    KANTSStatus k_ants_cancel_deploy()
    KANTSStatus k_ants_get_deploy_status(uint16_t * resp)
    KANTSStatus k_ants_get_uptime(uint32_t * uptime)
    KANTSStatus k_ants_get_system_telemetry(ants_telemetry * telem)
    KANTSStatus k_ants_get_activation_count(KANTSAnt antenna, uint8_t * count)
    KANTSStatus k_ants_get_activation_time(KANTSAnt antenna, uint16_t * time)
    KANTSStatus k_ants_watchdog_kick()
    KANTSStatus k_ants_watchdog_start()
    KANTSStatus k_ants_watchdog_stop()
    KANTSStatus k_ants_passthrough(const uint8_t * tx, int tx_len, uint8_t * rx,int rx_len)
    
    
def py_k_ants_init(char * bus, uint8_t primary, uint8_t secondary, uint8_t ant_count, uint32_t timeout):
    return k_ants_init(bus,primary,secondary,ant_count,timeout)
def py_k_ants_terminate():
    k_ants_terminate()
def py_k_ants_configure(KANTSController config):
    return k_ants_configure(config)
def py_k_ants_reset():
    return k_ants_reset()
def py_k_ants_arm():
    return k_ants_arm()
def py_k_ants_disarm():
    return k_ants_disarm()
def py_k_ants_deploy(antenna, override, timeout):
    return k_ants_deploy(<KANTSAnt>antenna,<bool>override,<uint8_t>timeout)
def py_k_ants_auto_deploy(timeout):
    return k_ants_auto_deploy(<uint8_t>timeout)
def py_k_ants_cancel_deploy():
    return k_ants_cancel_deploy()
def py_k_ants_get_deploy_status(int resp):
    return k_ants_get_deploy_status(<uint16_t *>resp)
def py_k_ants_get_uptime( int uptime):
    return k_ants_get_uptime(<uint32_t *>uptime)
def py_k_ants_get_system_telemetry(telem):
    return k_ants_get_system_telemetry(<ants_telemetry *>telem)
def py_k_ants_get_activation_count(antenna, count):
    return k_ants_get_activation_count(<KANTSAnt>antenna,<uint8_t *>count)
def py_k_ants_get_activation_time(antenna, int time):
    return k_ants_get_activation_time(<KANTSAnt>antenna,<uint16_t *>time)
def py_k_ants_watchdog_kick():
    return k_ants_watchdog_kick()
def py_k_ants_watchdog_start():
    return k_ants_watchdog_start()
def py_k_ants_watchdog_stop():
    return k_ants_watchdog_stop()
def py_k_ants_passthrough(tx, tx_len,rx,rx_len):
    return k_ants_passthrough(<const uint8_t *>tx,<int>tx_len,<uint8_t *>rx,<int>rx_len)
def py_k_i2c_init(device, int fp):
    return k_i2c_init(<char *>device, <int *>fp)
def py_k_i2c_terminate(int fp):
    k_i2c_terminate(<int *>fp)
def py_k_i2c_write(i2c, addr, ptr, len):
    return k_i2c_write(<int>i2c, <uint16_t>addr, <uint8_t *>ptr, <int>len)
def py_k_i2c_read( i2c, addr, ptr, int len):
    return k_i2c_read(<int>i2c, <uint16_t>addr, <uint8_t *>ptr, <int>len)
