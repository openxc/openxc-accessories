#!/usr/bin/python

# $Rev:: 382           $
# $Author:: mlgantra   $
# $Date:: 2015-06-23 1#$
#
# openXC-modem main function

import logging
import Queue
import threading
import time

from xcmodem_common import *
from xcmodem_vi import *
from xcmodem_app import *
import xcmodem_ver

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger('xcmodem')

try: 
    import bluetooth
except ImportError:
    LOG.debug("pybluez library not installed, can't use bluetooth interface")
    bluetooth = None


def main(sdebug = 0, debug = 0):
    first = 1
    attempt = 1
    threads = []
    v2x = boardid_inquiry() == 2
    if v2x:
        sys.path.append('../v2x')              # V2X specific
        import xcmodem_md
        import xcmodem_mk5

    LOG.info("OpenXCModem Embedded Software - Rev %s" % xcmodem_ver.get_version())

    pairing_registration()
    vi_cleanup()
    vi_dev = xcModemVi(port_dict['vi_app']['port'], vi_in_queue, vi_out_queue, sdebug, debug)

    while True:
        if (vi_dev.vi_main() or modem_state['vi_app'] == vi_state.DISABLE):
            if first:
                first = 0
                LOG.info("App Tasks ...")
                # Android/Mobil App thread
                if port_dict['mb_app']['enable']:
                    thread = appThread('mb_app', port_dict['mb_app']['port'], mb_in_queue, mb_out_queue, mb_passthru_queue, vi_out_queue)
                    thread.start()
                    threads.append(thread)

                if port_dict['md_app']['enable']:
                    if v2x:
                        # V2X-MD Master/Client thread
                        thread = xcmodem_md.xcModemMDthread(conf_options['openxc_md_mac'], port_dict['md_app']['port'],
                                                            md_in_queue, md_out_queue, debug)
                    else:
                        # V2X-MD Slave/Server App thread
                        thread = appThread('md_app', port_dict['md_app']['port'], md_in_queue, md_out_queue, md_passthru_queue, vi_out_queue)
                    thread.start()
                    threads.append(thread)

                if v2x:
                    # V2X-V2X MK5 thread
                    thread = xcmodem_mk5.mk5Thread('wf_app', wf_in_queue, wf_out_queue)
                    thread.start()
                    threads.append(thread)

                # GPS thread
                if conf_options['gps_enable']:
                    sys.path.append('../modem')                # GPS is only supported in modem
                    import xcmodem_gps
                    thread = xcmodem_gps.gpsThread(sdebug, debug)
                    thread.start()
                    threads.append(thread)

            while not exit_flag['vi_app']:
                if not vi_in_queue.empty():
                    data = vi_in_queue.get()
                    if modem_state['md_app'] == md_state.OPERATION:
                        if passthru_flag['md_app']:
                            md_passthru_queue.put(data)
                    if modem_state['mb_app'] == app_state.OPERATION:
                        if passthru_flag['mb_app']:
                            mb_passthru_queue.put(data)
                    # and dump to trace file
                    vi_dev.trace_raw_lock.acquire()
                    if vi_dev.fp and vi_dev.trace_enable:
                        new = vi_dev.vi_timestamp(data)
                        vi_dev.fp.write(new)
                    vi_dev.trace_raw_lock.release()
                else:
                    msleep(1)

            modem_state['vi_app'] = vi_state.LOST
            vi_dev.lost_cnt += 1
            LOG.info("vi_app state %s %d time" % (modem_state['vi_app'], vi_dev.lost_cnt))
            vi_dev.vi_exit()
            # flush passthru queues
            while not md_passthru_queue.empty():
                md_passthru_queue.get()
            while not mb_passthru_queue.empty():
                mb_passthru_queue.get()

        if exit_flag['all_app']:
            LOG.debug("Ending all_app")
            break;
        time.sleep(float(conf_options['openxc_vi_discovery_interval']))
        attempt += 1
        if (attempt > MAX_BRING_UP_ATTEMPT):
            LOG.debug("vi_app max out %d attempts" % MAX_BRING_UP_ATTEMPT)
            break;

    # terminate all threads
    for k in exit_flag.keys():
        exit_flag[k] = 1

    # Wait for all threads to complete
    for t in threads:
        t.join()

    LOG.info("Ending xcmodem")
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', help='Verbosity Level (-2..2)')
    args = parser.parse_args()

    if args.v is None:
        level = 0
    else:
        level = int(args.v)

    if level < -1:
        LOG.setLevel(level=logging.WARN)
    elif level < 0:
        LOG.setLevel(level=logging.INFO)
    main(sdebug = (level>1), debug = (level>0))
