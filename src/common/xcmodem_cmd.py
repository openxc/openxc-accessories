#!/usr/bin/python

# $Rev:: 371           $
# $Author:: mlgantra   $
# $Date:: 2015-06-19 1#$
#
# openXC-modem application agents command handlers


import argparse
import time
import re
import sys
import socket
import subprocess

from xcmodem_common import *
import xcmodem_ver

############################
# For MB_APP 
############################
def mb_parse_options(list):
    # Utilize argparse for command usage information
    parser = argparse.ArgumentParser(
            description="xc modem interface command handler", prog="xcmodem mb")
    parser.add_argument("command_type", type=str, choices=['command','modem_command'])
    parser.add_argument("modem_commands", type=str, choices=['device_id', 'version','diagnostics_enable','diagnostics_disable'])
    return parser.parse_args(list)


DIAG_SCREEN_UPDATE_INTERVAL = 0.5

def mb_diagnostic_screen(v2x, name, outQ):
    while vi_bypass[name]:
        for l in modem_state.items():
            if not vi_bypass[name]:
                break
            (key, val) = l
            if v2x and (key == 'gps_app' or key == 'gsm_app'):       # skip V2X un-support apps
                continue
            tstamp = time.time()
            reply = '{"modem_label":"%s.state","modem_value":"%s","timestamp":%f}\0' % (key, val, tstamp)
            outQ.put(reply)

        for l in port_mac.items():
            if not vi_bypass[name]:
                break
            (key, val) = l
            tstamp = time.time()
            reply = '{"modem_label":"%s.mac","modem_value":"%s","timestamp":%f}\0' % (key, val, tstamp)
            outQ.put(reply)
   
        for l in md_dict.items():
            if not vi_bypass[name]:
                break
            (key, val) = l
            tstamp = time.time()
            reply = '{"modem_label":"md_app.%s","modem_value":"%s","timestamp":%f}\0' % (key, val, tstamp)
            outQ.put(reply)

        if v2x:
            for l in wf_dict.items():
                if not vi_bypass[name]:
                    break
                (key, val) = l
                tstamp = time.time()
                reply = '{"modem_label":"wf_app.%s","modem_value":"%s","timestamp":%f}\0' % (key, val, tstamp)
                outQ.put(reply)
    
        if conf_options['gps_enable'] and not v2x:
            for l in gps_dict.items():
                if not vi_bypass[name]:
                    break
                (key, val) = l
                tstamp = time.time()
                reply = '{"modem_label":"gps.%s","modem_value":"%s","timestamp":%f}\0' % (key, val, tstamp)
                outQ.put(reply)
   
        if conf_options['gsm_enable'] and not v2x:
            for l in gsm_dict.items():
                if not vi_bypass[name]:
                    break
                (key, val) = l
                tstamp = time.time()
                reply = '{"modem_label":"gsm.%s","modem_value":"%s","timestamp":%f}\0' % (key, val, tstamp)
                outQ.put(reply)

        for l in conf_options.items():
            if not vi_bypass[name]:
                break
            (key, val) = l
            if v2x and (key == 'gps_enable' or key == 'gsm_enable'): # skip V2X un-support apps
                continue
            tstamp = time.time()
            if re.search(r'_interval', key, re.M|re.I) \
                or re.search(r'_duration', key, re.M|re.I) \
                or re.search(r'_size', key, re.M|re.I) :
                reply = '{"modem_label":"%s","modem_value":%d,"timestamp":%f}\0' % (key, int(val), tstamp)
            else:
                reply = '{"modem_label":"%s","modem_value":"%s","timestamp":%f}\0' % (key, val, tstamp)
            outQ.put(reply)
        time.sleep(DIAG_SCREEN_UPDATE_INTERVAL)


def mb_commands_handler(v2x, name, stop_event, outQ, cmd):
    bypass_mode = vi_bypass[name]
    diag_start = False
    if cmd == 'device_id':
        value = socket.gethostname()
    elif cmd == 'version':
        value = xcmodem_ver.get_version()
    elif cmd == 'diagnostics_enable':
        value = None
        if not bypass_mode:
            diag_start = True
        bypass_mode = True
    elif cmd == 'diagnostics_disable':
        value = None
        if stop_event is not None:
            stop_event.set()                # terminate mb_diagnostic_screen thread
            stop_event = None
        bypass_mode = False

    if value is not None:
        reply = '{"modem_command_response":"%s","modem_message":"%s","status":true}\0' % (cmd, value)
    else:
        reply = '{"modem_command_response":"%s","status":true}\0' % cmd
    outQ.put(reply)
    vi_bypass[name] = bypass_mode
    if diag_start:
        thread, stop_event = loop_timer(None, mb_diagnostic_screen, v2x, name, outQ)


def combined_command_handler(list, str):
    # To handle combined command in one line
    l = re.search('}\W*{', str)
    if l:
        list.append(str[:l.start()+1])
        combined_command_handler(list, str[l.end()-1:])
    else:
        list.append(str)


def mb_process_data(v2x, name, outQ, passQ, data):
    # Limitation: don't handle partial command string
    stop_event = None

    command_list = []
    combined_command_handler(command_list, data)    # break into single commands list
    for line in command_list:
        try:
            list = re.sub('\W+'," ", line).split()
            arguments = mb_parse_options(list)
        except SystemExit:
            # LOG.error("Unknown command: " + line) - Not really an error
            # pass it thru anyway
            passQ.put(line)
            LOG.debug("pass: [%s]" % line)
            return 0
        else:
            if arguments.command_type == 'command':
                passQ.put(line)
                LOG.debug("pass: [%s]" % line)
                pass
            else:
                stop_event = mb_commands_handler(v2x, name, stop_event, outQ, arguments.modem_commands)
    return 0


############################
# For V2X-MD (communicate via BT)
# Leverage for V2X-V2X as well which communicate via Wifi
# For simplicity, there is no ack message
############################
def md_parse_request_options(list):
    # Utilize argparse for command usage information
    parser = argparse.ArgumentParser(
            description="xcmodem interface command handler", prog="xcmodem md")
    parser.add_argument("command_type", type=str, choices=['modem_command'])
    parser.add_argument("commands", type=str, choices=['device_id', 'version', 'heartbeat'])
    return parser.parse_args(list)


def md_parse_response_options(list):
    # Utilize argparse for command usage information
    parser = argparse.ArgumentParser(
            description="xcmodem interface command handler", prog="xcmodem md")
    parser.add_argument("command_type", type=str, choices=['modem_command_response'])
    parser.add_argument("commands", type=str, choices=['device_id', 'version', 'heartbeat'])
    parser.add_argument("value_key", type=str, choices=['modem_message'])
    parser.add_argument("value")
    parser.add_argument("status_key", type=str, choices=['status'])
    parser.add_argument("status", type=str, choices=['true','false'])
    return parser.parse_args(list)


def md_request_commands_handler(v2x, name, outQ, req):
    if req == 'device_id':
        value = socket.gethostname()
    elif req == 'version':
        value = xcmodem_ver.get_version()
    elif req == 'heartbeat':
        value = time.time()
    reply = '{"modem_command_response":"%s","modem_message":"%s","status":true}\0' % (req, value)
    outQ.put(reply)


def md_response_commands_handler(v2x, name, outQ, resp, val):
    if resp == 'device_id':
        md_dict['id'] = val
    elif resp == 'version':
        md_dict['ver'] = val
    elif resp == 'heartbeat':
        md_dict['hbeat'] = val
        if v2x:
           # synch clock 
           date = time.strftime("%a %b %d %Y %H:%M:%S %Z", time.localtime(float(val)))
           cmd = "date -s '%s'" % date
           # LOG.debug(" issuing " + cmd)
           subprocess.call(cmd, shell=True, stdout=subprocess.PIPE)


def md_process_data(v2x, name, outQ, passQ, data):
    command_list = []
    combined_command_handler(command_list, data)    # break into single commands list
    for line in command_list:
        try:
            list = re.sub('["{}:,\0]'," ", line).split()
            if list[0] == 'modem_command':
                arguments = md_parse_request_options(list)
            else:
                arguments = md_parse_response_options(list)
        except SystemExit:
            LOG.error("%s Unknown command: %s" % (name, line)) 
            return 0
        else:
            if arguments.command_type == 'modem_command':
                md_request_commands_handler(v2x, name, outQ, arguments.commands)
            else:
                md_response_commands_handler(v2x, name, outQ, arguments.commands, arguments.value)
    return 0


def mk5_response_commands_handler(name, outQ, resp, val):
    if resp == 'device_id':
        wf_dict['id'] = val
    elif resp == 'version':
        wf_dict['ver'] = val
    elif resp == 'heartbeat':
        wf_dict['hbeat'] = val


def mk5_process_data(name, outQ, data):
    command_list = []
    combined_command_handler(command_list, data)    # break into single commands list
    for line in command_list:
        try:
            list = re.sub('["{}:,\0]'," ", line).split()
            if list[0] == 'modem_command':
                arguments = md_parse_request_options(list)
            else:
                arguments = md_parse_response_options(list)
        except SystemExit:
            LOG.error("%s Unknown command: %s" % (name, line)) 
            return 0
        else:
            if arguments.command_type == 'modem_command':
                md_request_commands_handler(1, name, outQ, arguments.commands)
            else:
                mk5_response_commands_handler(name, outQ, arguments.commands, arguments.value)
    return 0


############################
# Unit test
############################
def test_drain(queue):
    while True:
        while not queue.empty():
            data = queue.get()
            print("send: [%s]" % data)

def test_main():
    v2x = boardid_inquiry(1) == 2
    outQ = Queue.Queue()
    passQ = Queue.Queue()
    thread1, stop_out = loop_timer(None, test_drain, outQ)           # thread to drain outQ
    thread2, stop_pass = loop_timer(None, test_drain, passQ)         # thread to drain passQ

    name = 'md_app'
    md_process_data(v2x, name, outQ, passQ,'{"modem_command_response":"device_id","modem_message":"OpenXC-VI-V2X-F6BF","status":true}')
    md_process_data(v2x, name, outQ, passQ,'{"modem_command_response":"version","modem_message":"0.1.4","status":true}{"modem_command_response":"device_id","modem_message":"OpenXC-VI-V2X-F6BF","status":true}')
    md_process_data(v2x, name, outQ, passQ,'{"modem_command_response":"heartbeat","modem_message":1433963900.462915,"status":true}')
    md_process_data(v2x, name, outQ, passQ,'{modem_command":"version"}')
    md_process_data(v2x, name, outQ, passQ,'{modem_command":"device_id"}')
    md_process_data(v2x, name, outQ, passQ,'{modem_command":"heartbeat"}')

    name = 'wf_app'
    mk5_process_data(name, outQ, '{"modem_command_response":"version","modem_message":"0.1.4","status":true}{"modem_command_response":"device_id","modem_message":"OpenXC-VI-V2X-F6BF","status":true}')
    mk5_process_data(name, outQ, '{modem_command":"heartbeat"}')

    name = 'mb_app'
    mb_process_data(v2x, name, outQ, passQ,'{"command":"version"}{"command":"device_id"}')
    mb_process_data(v2x, name, outQ, passQ,'{"abc":"device_id"}')
    mb_process_data(v2x, name, outQ, passQ,'{"modem_command":"device_id"}')
    mb_process_data(v2x, name, outQ, passQ,'{"command":"device_id"}')
    mb_process_data(v2x, name, outQ, passQ,'{"modem_command":"version"}')
    mb_process_data(v2x, name, outQ, passQ,'{"modem_command":"diagnostics_enable"}')
    mb_process_data(v2x, name, outQ, passQ,'{"modem_label":"accelerator_pedal_position","modem_value":0,"timestamp":1364323939.012000}')
    time.sleep(5)
    mb_process_data(v2x, name, outQ, passQ,'{"modem_command":"diagnostics_disable"}')
    mb_process_data(v2x, name, outQ, passQ,'{"command":"version"}')
    mb_process_data(v2x, name, outQ, passQ,'{"modem_command":"diagnostics_enable"}')
    mb_process_data(v2x, name, outQ, passQ,'{"modem_command":"diagnostics_disable"}')

    stop_out.set()
    stop_pass.set()
    time.sleep(1)

if __name__ == '__main__':
    test_main()
