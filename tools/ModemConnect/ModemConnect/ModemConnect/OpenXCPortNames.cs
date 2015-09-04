using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using Microsoft.Win32;
using log4net;

namespace ModemConnect
{
    static class OpenXCPortNames
    {
        private static readonly ILog _Logger = LogManager.GetLogger(typeof(OpenXCPortNames));

        /// <summary>
        /// Compile an array of COM port names associated with given VID and PID
        /// </summary>
        /// <param name="vid"></param>
        /// <param name="pid"></param>
        /// <returns></returns>
        static public List<string> GetOpenXCPorts(String vid, String pid)
        {
            _Logger.Info("Getting OpenXC ports listing.");
            var pattern = String.Format("^VID_{0}.PID_{1}", vid, pid);
            var rx = new Regex(pattern, RegexOptions.IgnoreCase);
            var comports = new List<string>();
            var rk1 = Registry.LocalMachine;
            var rk2 = rk1.OpenSubKey("SYSTEM\\CurrentControlSet\\Enum");
            if (rk2 != null)
            {
                foreach (var s3 in rk2.GetSubKeyNames())
                {
                    var rk3 = rk2.OpenSubKey(s3);
                    if (rk3 != null)
                    {
                        foreach (var s in rk3.GetSubKeyNames())
                        {
                            if (rx.Match(s).Success)
                            {
                                var rk4 = rk3.OpenSubKey(s);
                                if (rk4 != null)
                                {
                                    foreach (var s2 in rk4.GetSubKeyNames())
                                    {
                                        var rk5 = rk4.OpenSubKey(s2);
                                        if (rk5 != null)
                                        {
                                            var rk6 = rk5.OpenSubKey("Device Parameters");
                                            if (rk6 != null)
                                            {
                                                comports.Add((string) rk6.GetValue("PortName"));
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            _Logger.Debug("GetOpenXCPorts: " + comports);

            return comports;
        }
    }
}
