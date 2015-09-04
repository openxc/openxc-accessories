#!/usr/bin/python

# $Rev:: 375           $
# $Author:: mlgantra   $
# $Date:: 2015-06-19 1#$
#
# openXC-modem application slave/server agents thread and associated functions

import Queue
import threading
import time
import subprocess

from xcmodem_common import *
from xcmodem_cmd import *
from xcmodem_vi import vi_cleanup


APP_RECONNECT = True

try:
    import bluetooth
except ImportError:
    LOG.debug("pybluez library not installed, can't use bluetooth interface")
    bluetooth = None


def sdp_prep(port):
    # SDP queries on bluetooth devices
    cmd = 'sdptool browse local | grep "Channel: %s"' % port
    # LOG.debug("issuing: " + cmd)
    if subprocess.call(cmd, shell=True, stdout=subprocess.PIPE):
        cmd = 'sdptool add --channel=%s SP' % port
        # LOG.debug("issuing: " + cmd)
        subprocess.call(cmd, shell=True, stdout=subprocess.PIPE)


def app_listening(name, port):
    # Establish server/slave port listenning
    serverSock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSock.bind(("", port))
    LOG.debug("Listen on port %s" % port)
    # OXM-72: use timeout to break listening socket so we can restart bluetooth
    serverSock.settimeout(1)
    serverSock.listen(1)
    while True:
        try:
            clientSock,address = serverSock.accept()
        except BluetoothError as e:
            # socket.timeout is presented as BluetoothError w/o errno
            if e.args[0] == 'timed out':
                if not exit_flag['bt_restart']:
                    continue
                LOG.debug("timeout stop " + name)
            else:
                LOG.debug("%s %s" % (name, e))
            exit_flag[name] = 1
            serverSock.shutdown(socket.SHUT_RDWR)
            serverSock.close()
            return (None, None, None)
        else:
            break
    LOG.info("Accepted connection from %s", address)
    return (serverSock, clientSock, address)


class appThread (threading.Thread):
    def __init__(self, name, port, inQ, outQ, passthruQ, passQ):
        threading.Thread.__init__(self)
        self.name = name
        self.port = port
        self.inQ = inQ
        self.outQ = outQ
        self.passthruQ = passthruQ
        self.passQ = passQ
        self.running = True
        self.v2x = boardid_inquiry() == 2 
        self.threads = []

    def run(self):
        while not exit_flag['all_app']:
            # OXM-72: not start until bt_restart done
            while exit_flag['bt_restart']:
                time.sleep(1)
            LOG.debug("Starting " + self.name)

            modem_state[self.name] = app_state.PENDING
            exit_flag[self.name] = 0

            while not exit_flag['all_app']:
                # OXM-72: need to prep sdp again since BT might have just been restarted
                sdp_prep(self.port)
                serverSock, clientSock, address = app_listening(self.name, self.port)

                # OXM-72: listening socket might be timeout with exit_flag 
                if exit_flag[self.name]:
                    break

                # Paired devices might incidently connect to the reserved port
                # Thus, we need to check for authorize device
                addr = address[0]
                cmd = "bluez-test-device list | awk '/%s/ {print $2}'" % addr
                # LOG.debug("issuing " + cmd)
                device = subprocess.check_output(cmd, shell=True).split()[0]
                if (self.name == 'mb_app' and \
                    not device.startswith(OPENXC_DEVICE_NAME_PREFIX)) or \
                   (self.name == 'md_app' and \
                    device.startswith(OPENXC_V2X_NAME_PREFIX)):
                    break
                LOG.debug("%s unpair un-authorized connection %s %s" % (self.name, device, address))
                cmd = "bluez-test-device remove " + addr
                # LOG.debug("issuing " + cmd)
                if subprocess.call(cmd, shell=True):
                    LOG.debug(self.name + " fail to unpair unauthorized device")
                clientSock.shutdown(socket.SHUT_RDWR)
                clientSock.close()
                serverSock.shutdown(socket.SHUT_RDWR)
                serverSock.close()

            # OXM-72: listening socket might be timeout with exit_flag 
            if exit_flag[self.name]:
                LOG.debug("Ending " + self.name)
                continue

            modem_state[self.name] = app_state.CONNECTED
            port_mac[self.name] = addr

            # create new threads
            thread1 = sockRecvThread("%s-Recv" % self.name, clientSock, self.inQ, self.name)
            thread2 = sockMergeSendThread("%s-Send" % self.name, clientSock, self.passthruQ, self.outQ, self.name)
            # start threads
            thread1.start()
            thread2.start()

            self.threads.append(thread1)
            self.threads.append(thread2)

            # Acquire md_app info
            if self.name == 'md_app':
                self.outQ.put('{"modem_command":"device_id"}\0')
                self.outQ.put('{"modem_command":"version"}\0')

            modem_state[self.name] = app_state.OPERATION

            while not exit_flag[self.name]:
                if not self.inQ.empty():
                    cmd = self.inQ.get()
                    if self.name == 'mb_app':
                        LOG.debug("%s proc [%s]" % (self.name,cmd))
                        mb_process_data(self.v2x, self.name, self.outQ, self.passQ, cmd)
                    elif self.name == 'md_app':
                        md_process_data(self.v2x, self.name, self.outQ, self.passQ, cmd)
                msleep(1)

            # waif for threads finish
            for t in self.threads:
                t.join()
            clientSock.shutdown(socket.SHUT_RDWR)
            clientSock.close()
            serverSock.shutdown(socket.SHUT_RDWR)
            serverSock.close()
            # flush the queues
            while not self.inQ.empty():
                self.inQ.get()
            while not self.outQ.empty():
                self.outQ.get()
            while not self.passthruQ.empty():
                self.passthruQ.get()
            LOG.debug("Ending " + self.name)
            modem_state[self.name] = app_state.DONE
            if not APP_RECONNECT:
                break;
            time.sleep(1)


if __name__ == '__main__':
    threads = []
    pairing_registration()
    vi_cleanup()

    # Enable both app port for testing purpose
    port_dict['md_app']['enable'] = 1

    boardid_inquiry(1)
    if port_dict['mb_app']['enable']:
        thread = appThread('mb_app', port_dict['mb_app']['port'], mb_in_queue, mb_out_queue, mb_passthru_queue, vi_out_queue)
        thread.start()
        threads.append(thread)

    if port_dict['md_app']['enable']:
        thread = appThread('md_app', port_dict['md_app']['port'], md_in_queue, md_out_queue, md_passthru_queue, vi_out_queue)
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for t in threads:
        t.join()

    LOG.info("Exiting Main Thread")
