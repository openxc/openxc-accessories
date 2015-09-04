using System;
using System.Collections.Generic;
using System.Linq;
using System.Management;
using System.Text.RegularExpressions;
using log4net;

namespace ModemConnect
{
    public static class SerialPortService
    {
        private static string[] _SerialPorts;

        private static ManagementEventWatcher _Arrival;

        private static ManagementEventWatcher _Removal;

        private static readonly ILog _Logger = LogManager.GetLogger(typeof(SerialPortService));

        static SerialPortService()
        {
            _Logger.Info("Serial Port");
            _SerialPorts = GetAvailableSerialPorts();
            MonitorDeviceChanges();
        }

        /// <summary>
        /// If this method isn't called, an InvalidComObjectException will be thrown (like below):
        /// System.Runtime.InteropServices.InvalidComObjectException was unhandled
        ///Message=COM object that has been separated from its underlying RCW cannot be used.
        ///Source=mscorlib
        ///StackTrace:
        ///     at System.StubHelpers.StubHelpers.StubRegisterRCW(Object pThis, IntPtr pThread)
        ///     at System.Management.IWbemServices.CancelAsyncCall_(IWbemObjectSink pSink)
        ///     at System.Management.SinkForEventQuery.Cancel()
        ///     at System.Management.ManagementEventWatcher.Stop()
        ///     at System.Management.ManagementEventWatcher.Finalize()
        ///InnerException: 
        /// </summary>
        public static void CleanUp()
        {
            _Arrival.Stop();
            _Removal.Stop();
        }

        public static event EventHandler<PortsChangedArgs> PortsChanged;

        private static void MonitorDeviceChanges()
        {
            try
            {
                var deviceArrivalQuery = new WqlEventQuery("SELECT * FROM Win32_DeviceChangeEvent WHERE EventType = 2");
                var deviceRemovalQuery = new WqlEventQuery("SELECT * FROM Win32_DeviceChangeEvent WHERE EventType = 3");

                _Arrival = new ManagementEventWatcher(deviceArrivalQuery);
                _Removal = new ManagementEventWatcher(deviceRemovalQuery);

                _Arrival.EventArrived += (o, args) => RaisePortsChangedIfNecessary(EventType.Insertion);
                _Removal.EventArrived += (sender, eventArgs) => RaisePortsChangedIfNecessary(EventType.Removal);

                // Start listening for events
                _Arrival.Start();
                _Removal.Start();
            }
            catch (ManagementException)
            {

            }
        }

        private static void RaisePortsChangedIfNecessary(EventType eventType)
        {
            lock (_SerialPorts)
            {
                var availableSerialPorts = GetAvailableSerialPorts();
                if (!_SerialPorts.SequenceEqual(availableSerialPorts))
                {
                    _SerialPorts = availableSerialPorts;
                    PortsChanged.Raise(null, new PortsChangedArgs(eventType, _SerialPorts));
                }
            }
        }

        /// <summary>
        /// Tell subscribers, if any, that this event has been raised.
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <param name="handler">The generic event handler</param>
        /// <param name="sender">this or null, usually</param>
        /// <param name="args">Whatever you want sent</param>
        public static void Raise<T>(this EventHandler<T> handler, object sender, T args) where T : EventArgs
        {
            // Copy to temp var to be thread-safe (taken from C# 3.0 Cookbook - don't know if it's true)
            EventHandler<T> copy = handler;
            if (copy != null)
            {
                copy(sender, args);
            }
        }

        public static string[] GetAvailableSerialPorts()
        {
            return GetUSBCOMDevices();
        }

        static string[] GetUSBCOMDevices()
        {
            var list = new List<string>();

            _Logger.Info("Getting list of USB COM devices.");

            var searcher2 = new ManagementObjectSearcher("SELECT * FROM Win32_PnPEntity where deviceid like 'USB%'");
            
            foreach (ManagementObject mo2 in searcher2.Get())
            {
                _Logger.Info("ManagementObject: " + mo2);

                var nameObject = mo2["Name"];
                if (nameObject != null)
                {
                    var name = nameObject.ToString();

                    // Extract the "COM12", for example, from "ELMO GMAS (COM12)" (or similar).
                    var r = new Regex(@"\((?<shortname>[^\)]*)\)", RegexOptions.IgnoreCase);
                    
                    // Name will have a substring like "(COM12)" in it.
                    if (name.Contains("(COM"))
                    {
                        var m = r.Match(name);
                        if (m.Success)
                        {
                            list.Add(m.Groups["shortname"].Value);
                        }
                        list.Add(name);
                    }
                }
                else
                {
                    _Logger.Info("MO has no name.");
                }
            }

            _Logger.Info("Collected device list...filtering.");

            // remove duplicates, sort alphabetically and convert to array
            var usbDevices = list.Distinct().OrderBy(s => s).ToArray();

            var deviceList = (usbDevices.Length != 0 )? String.Empty : "(none)";
            foreach (var usbDevice in usbDevices)
            {
                deviceList += usbDevice + " ";
            }

            _Logger.Info("USB COM Devices: " + deviceList);

            return usbDevices;
        }
    }
}
