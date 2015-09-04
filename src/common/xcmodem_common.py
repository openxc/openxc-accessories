# $Rev:: 390           $
# $Author:: mlgantra   $
# $Date:: 2015-06-24 1#$
#
# openXC-modem common functions

import Queue
import threading
import time
import argparse
import logging
import logging.handlers
import subprocess
import os
import re

from bluetooth.btcommon import BluetoothError


logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger('xcmodem')

# 
# Add the log message handler to the logger
# We can also perform logging into a separate rotating file, ie:
#
# LOG_FILENAME = "/var/log/xcmodem.log"
# fh = logging.handlers.RotatingFileHandler(
#              LOG_FILENAME, maxBytes=10240, backupCount=5)
# fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
# LOG.addHandler(fh)

#
# logging into /var/log/syslog
#  
sh = logging.handlers.SysLogHandler(address = '/dev/log')
sh.setFormatter(logging.Formatter('%(name)s[%(process)d] - %(levelname)s - %(message)s'))
LOG.addHandler(sh)



def configure_logging(level=logging.WARN):
    logging.getLogger("xcmodem").addHandler(logging.StreamHandler())
    logging.getLogger("xcmodem").setLevel(level)



OPENXC_V2X_NAME_PREFIX = "OpenXC-VI-V2X-"
OPENXC_MODEM_NAME_PREFIX = "OpenXC-VI-MODEM-"
OPENXC_DEVICE_NAME_PREFIX = "OpenXC-VI-"


MAX_DISCOVERY_ATTEMPT = 3
MAX_CONNECTION_ATTEMPT = 3
MAX_BRING_UP_ATTEMPT = 1000


SERIAL_INTERFACE_TIMEOUT = 0.3        # Should be enough to accomodate several requests per second


# Enum simple implement
class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

# OpenXC-vi_app status
vi_state = Enum(['IDLE', 'DISABLE', 'ADDR_INQUIRY', 'ADDR_ASSIGNED', 'DISCOVERED', 'CONNECTED', 'OPERATION', 'LOST', 'RESTART'])

# OpenXC-md_app status
md_state = Enum(['IDLE', 'DISABLE', 'ADDR_INQUIRY', 'ADDR_ASSIGNED', 'DISCOVERED', 'CONNECTED', 'OPERATION', 'LOST', 'RESTART'])

# App status
app_state = Enum(['IDLE', 'PENDING', 'CONNECTED', 'LOCKING', 'OPERATION', 'DONE', 'LOST'])

# Charger status
charge_state = Enum(['IDLE', 'NOT_CHARGE', 'PRE_CHARGE', 'FAST_CHARGE', 'CHARGE_DONE'])

# Use the hidden file .xcmodem_boardid to indicate the board type 
XCMODEM_BOARDID_FILE = '../common/.xcmodem_boardid'        # hidden file
board_type = {
    0:  {'type': 'MODEM-EVT', 'prefix': 'OpenXC-VI-MODEM'},  # OpenXC-Modem EVT
    1:  {'type': 'MODEM-DVT', 'prefix': 'OpenXC-VI-MODEM'},  # OpenXC-Modem DVT
    2:  {'type': 'V2X'      , 'prefix': 'OpenXC-VI-V2X'}     # OpenXC-V2X
}

# Static rfcomm port assignment
port_dict = {
    'vi_app': {'port': 1, 'enable': 1}, # for OpenXC_vi_app device
    'mb_app': {'port': 22,'enable': 1}, # for OpenXCModem Mobile Application
    'md_app': {'port': 23,'enable': 0}  # for OpenXCModem V2X-MD Application
}

# VI data stream pass-thru mode 
vi_bypass = {
    'mb_app': False,            # for OpenXCModem Mobile Application
    'md_app': True              # for OpenXCModem V2X-MD Application
}

# VI Passthru support nable flag 
passthru_enable = {
    'mb_app': 1,                # for OpenXCModem Mobile Application
    'md_app': 0                 # for OpenXCModem V2X-MD Application - No support
}

# Passthru effective flag
passthru_flag = {
    'mb_app': 0,                # for OpenXCModem Mobile Application
    'md_app': 0                 # for OpenXCModem V2X-MD Application
}

# port MAC status
port_mac = {
    'vi_app': None,             # for OpenXC_vi_app device
    'md_app': None,             # for OpenXCModem V2X-MD Application
    'mb_app': None,             # for OpenXCModem Mobile Application
    'wf_app': None              # for OpenXCModem WiFi/V2X Application
}

# V2X-MD app info
md_dict = {
    'id'   : None,
    'ver'  : None,
    'hbeat': None
}
    
# V2X-V2X app info
wf_dict = {
    'id'   : None,
    'ver'  : None,
    'hbeat': None
}

# Current modem state for diagnostic message
modem_state = {
    'vi_app' : vi_state.IDLE,
    'gps_app': app_state.IDLE,
    'gsm_app': app_state.IDLE,
    'md_app': md_state.IDLE,
    'mb_app': app_state.IDLE,
    'wf_app': app_state.IDLE,
    'charger': charge_state.IDLE
}

# Configuration File dictionary
conf_options = {
    'openxc_modem_mac' : 'None',                # self MAC 
    'openxc_md_mac' : 'None',                   # only appliable for V2X
    'openxc_md_enable' : 1,                     # 1/0 by default for Modem/V2X
    'openxc_vi_mac' : 'None',
    'openxc_vi_enable' : 1,                     # 1/0 by default for Modem/V2X
    'openxc_vi_trace_snapshot_duration' : 10,
    'openxc_vi_trace_idle_duration' : 110,
    'openxc_vi_trace_truncate_size' : 0,        # zero means no truncate
    'openxc_vi_trace_filter_script' : 'None',   # executable shell script
    'openxc_vi_trace_number_of_backup' : 0,     # zero means no backup
    'openxc_vi_trace_backup_overwrite_enable' : 0,
    'openxc_vi_discovery_interval' : 10,
    'web_scp_userid' : 'anonymous',
    'web_scp_pem' : 'None',
    'web_scp_apn' : 'apn',
    'web_scp_config_url' : 'ip_address:file',
    'web_scp_config_download_enable': 0,
    'web_scp_target_url' : 'ip_address:file',
    'web_scp_target_overwrite_enable': 1,
    'web_scp_trace_upload_enable': 0,
    'web_scp_trace_upload_interval': 3600,
    'web_scp_sw_latest_version_url': 'None',
    'fw_factory_reset_enable': 1,
    'power_saving_mode' : 'normal',
    'led_brightness' : 128,                     # for normal of power_saving_mode

    'gps_log_interval': 10,
    'gps_enable': 1,    # These are mainly for emulation purpose
    'gsm_enable': 1     # production board should be correctly configured
                        # based on modem/v2x board type (xcmodem_v2x)
}

# termination signal
exit_flag = {
    'vi_app' : 0,
    'md_app' : 0,
    'mb_app' : 0,
    'wf_app' : 0,
    'all_app': 0,       # force flag to terminate ALL app
    'bt_restart' : 0,   # force flag for BlueTooth restart
}

# gps information
gps_dict = {
    'utc' : None, 
    'date': None,
    'lat' : None,
    'lon' : None,
    'alt' : None
}

# gsm information
gsm_dict = {
    'rssi': None, 
    'ber' : None
}

# Power-saving mode (performance / normal / saving)
power_mode = {
    'performance': {'ppp_tear_off': 0, 'monitor_interval': 2, 'led_brightness' : 255},
    'normal':      {'ppp_tear_off': 0, 'monitor_interval': 5, 'led_brightness' : 128},
    'saving':      {'ppp_tear_off': 1, 'monitor_interval': 10, 'led_brightness': 0}
}

# LED directory path per boardid
led_path = {
    'bat_grn': { 0: 'd10_grn', 1: 'bat_grn'},
    'bat_red': { 0: 'd10_red', 1: 'bat_red'},
    'bt':      { 0: 'd11'    , 1: 'bt'},
    'gps':     { 0: 'd12'    , 1: 'gps'},
    'wifi':    { 0: 'd13'    , 1: 'wifi'},
    'gsm':     { 0: 'd14'    , 1: 'r2_3g'}
}


usleep = lambda x: time.sleep(x/1000000.0)
msleep = lambda x: time.sleep(x/1000.0)

# Socket handling threads
class sockSendThread (threading.Thread):
    def __init__(self, name, socket, queue, eflag):
        threading.Thread.__init__(self)
        self.name = name
        self.sock = socket
        self.queue = queue
        self.eflag = eflag
    def run(self):
        LOG.debug("Starting " + self.name)
        while not exit_flag[self.eflag]:
            while not self.queue.empty():
                try:
                    data = self.queue.get()
                    self.sock.send(data)
                    # print("%s [%s]\n" % (self.name, data))
                except IOError as e:
                    exit_flag[self.eflag] = 1
                    LOG.debug("%s %s" % (self.name, e))
                    break
            msleep(1)
        LOG.debug("disconnected " + self.name)

class sockRecvThread (threading.Thread):
    def __init__(self, name, socket, queue, eflag, sflag = 0):
        threading.Thread.__init__(self)
        self.name = name
        self.sock = socket
        self.queue = queue
        self.eflag = eflag
        self.sflag = sflag
    def run(self):
        LOG.debug("Starting " + self.name)
        self.sock.settimeout(1)
        while not exit_flag[self.eflag]:
            try:
                data = self.sock.recv(1024)
                # print("%s [%s]\n" % (self.name, data))
                self.queue.put(data)
            except BluetoothError as e:
                # socket.timeout is presented as BluetoothError w/o errno
                if e.args[0] == 'timed out':
                    if not self.sflag:
                        continue
                    LOG.debug("timeout stop " + self.name)
                else:
                    LOG.debug("%s %s" % (self.name, e))
                exit_flag[self.eflag] = 1
                break
        LOG.debug("disconnected " + self.name)

#
# Best attempt to insert message after terminator charactor '\0' 
# in live stream queue 
# Note:
# The live stream is interrupted during bypass mode; thus, fragment will occur 
# at when it resumes
#

def sockSend (name, sock, data, eflag):
    try:
        sock.send(data)
        # print("%s [%s]" % (name, data))
    except IOError as e:
        exit_flag[eflag] = 1
        LOG.debug("%s %s" % (name, e))
        return False
    return True

class sockMergeSendThread (threading.Thread):
    def __init__(self, name, socket, pt_queue, op_queue, eflag):
        threading.Thread.__init__(self)
        self.name = name
        self.sock = socket
        self.pt_queue = pt_queue
        self.op_queue = op_queue
        self.eflag = eflag

    def run(self):
        LOG.debug("Starting " + self.name)
        attempt = 0
        passthru_pending = 0
        while not exit_flag[self.eflag]:
            if passthru_flag[self.eflag]:
                while not self.pt_queue.empty():
                    attempt = 0
                    pt_data = self.pt_queue.get()
                    # print("pt [%s]" % pt_data)
                    if vi_bypass[self.eflag] and not passthru_pending:
                        #  drop passthru stream to use output stream
                        while not self.op_queue.empty():
                            op_data = self.op_queue.get()
                            if not sockSend(self.name, self.sock, op_data, self.eflag):
                                break
                            if not self.pt_queue.empty():
                                pt_data = self.pt_queue.get()    #  drop passthru stream
                                # print("pt [%s]" % pt_data)
                        if exit_flag[self.eflag]:
                            break
                    else:
                        # assume json messages stream always valid
                        if not self.op_queue.empty():
                            passthru_pending = 1
                            if re.search(r'\0', pt_data, re.M|re.I):
                                passthru_pending = 0
                                op_data = '\0%s' % self.op_queue.get()
                                data = pt_data.rsplit('\0', 1)[0] + op_data  # insert op_queue
                                if not sockSend(self.name, self.sock, data, self.eflag):
                                    break
                                while not self.op_queue.empty():
                                    op_data = self.op_queue.get()
                                    if not sockSend(self.name, self.sock, op_data, self.eflag):
                                        break
                                if exit_flag[self.eflag]:
                                    break
                                data = pt_data.rsplit('\0', 1)[1]  # resume pt_data
                                if not sockSend(self.name, self.sock, data, self.eflag):
                                    break
                            elif not sockSend(self.name, self.sock, pt_data, self.eflag):
                                break
                        elif not sockSend(self.name, self.sock, pt_data, self.eflag):
                            break
                    if exit_flag[self.eflag]:
                        break
                if attempt == 100:         # passthru queue apears to be stuck somehow
                                           # then flush output queue
                    LOG.debug("Passthru stuck !!! " + self.name)
                    while not self.op_queue.empty():
                        op_data = self.op_queue.get()
                        if not sockSend(self.name, self.sock, op_data, self.eflag):
                            break
                    attempt = 0
            else:
                while not self.op_queue.empty():
                    op_data = self.op_queue.get()
                    if not sockSend(self.name, self.sock, op_data, self.eflag):
                        break
            attempt += 1 
            msleep(1)
        LOG.debug("disconnected " + self.name)


def loop_timer(interval, function, *args, **kwargs):
    stop_event = threading.Event()

    def loop():        # do ... while implementation
        while True:
            function(*args, **kwargs)
            if stop_event.wait(interval):
                break

    t = threading.Thread(target=loop)
    t.daemon = True
    t.start()
    return t, stop_event


def pairing_registration():
     # Enable inquiry + pagge scan
     subprocess.call('hciconfig hci0 piscan noauth', shell=True)

     # Simple agent registration for bluetooth pairing
     cmd = 'ps a | grep "bluez-simple-agent" | grep -v grep'
     # LOG.debug("issuing '%s'" % cmd)
     if subprocess.call(cmd, shell=True, stdout=subprocess.PIPE):
        cmd = 'echo "1234" | bluez-simple-agent hci0 &'
        # LOG.debug("issuing '%s'" % cmd)
        subprocess.call(cmd, shell=True, stdout=subprocess.PIPE)


def boardid_inquiry(debug = 0):
    id = 0
    if os.path.exists(XCMODEM_BOARDID_FILE):
        cmd = "cat %s" % XCMODEM_BOARDID_FILE
        id = int(subprocess.check_output(cmd, shell=True).split()[0])
        if board_type.get(id) is None:
            LOG.error("%s isn't a valid board id in %s - skip it !!" % (id, XCMODEM_BOARDID_FILE))
            id = 0
    if debug:
        LOG.info("Board " + board_type[id]['type'])
    return id


# Global queue for passing data
vi_in_queue = Queue.Queue()
vi_out_queue = Queue.Queue()
mb_in_queue = Queue.Queue()  
mb_out_queue = Queue.Queue()
mb_passthru_queue = Queue.Queue()
md_in_queue = Queue.Queue()
md_out_queue = Queue.Queue()
md_passthru_queue = Queue.Queue()
wf_in_queue = Queue.Queue()
wf_out_queue = Queue.Queue()
