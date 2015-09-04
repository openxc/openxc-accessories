using System;
using System.IO;
using System.Xml;
using System.Xml.Serialization;

namespace ModemConnect
{
    [XmlType]
    public sealed class Configuration
    {
        static public Configuration GetInstance()
        {
            if (_Instance == null)
            {
                var configFile = GetConfigFileName();
                if (!File.Exists(configFile))
                {
                    var defaultConfig = new Configuration();
                    defaultConfig.SaveAs(configFile);
                }

                _Instance = ConstructFrom(configFile);
            }

            return _Instance;
        }

        public static string GetConfigFileName()
        {
            var appData = Environment.ExpandEnvironmentVariables("%AppData%");
            var configFile = appData + "\\OpenXC\\ModemConnect\\ModemConnect.xml";
            return configFile;
        }

        private static Configuration _Instance;

        /// <summary>
        /// Create an instance.
        /// </summary>
        private Configuration()
        {
            TerminalApplicationPath = @"C:\Program Files (x86)\teraterm\ttermpro.exe";
            TerminalApplicationName = @"Teraterm";
            VID = "0525";
            PID = "A4A7";
            PortOption = "/C=";
            PortPrefix = ""; // e.g. COM (for COM9)
            PortNumber = "";
            BaudRateOption = "/BAUD=";
            BaudRate = "115200";
            ExtraArgs = "";
        }

        [XmlElement]
        public string TerminalApplicationPath { get; set; }

        [XmlElement]
        public string TerminalApplicationName { get; set; }

        [XmlElement]
        public string VID { get; set; }

        [XmlElement]
        public string PID { get; set; }

        [XmlElement]
        public string PortOption { get; set; }

        [XmlElement]
        public string PortPrefix { get; set; }
        
        [XmlElement]
        public string PortNumber { get; set; }

        [XmlElement]
        public string BaudRateOption { get; set; }

        [XmlElement]
        public string BaudRate { get; set; }

        [XmlElement]
        public string ExtraArgs { get; set; }

        /// <summary>
        /// Create an instance from the data in the given configFile.
        /// </summary>
        /// <param name="configFile">Fully qualified path name for configuration data file</param>
        /// <returns></returns>
        public static Configuration ConstructFrom(string configFile)
        {
            try
            {
                using (var tr = new XmlTextReader(configFile))
                {
                    var serializer = new XmlSerializer(typeof(Configuration));
                    return (Configuration)serializer.Deserialize(tr);
                }
            }
            catch (Exception ex)
            {
                throw new ArgumentException(String.Format("Cannot construct configuration data from {0}", configFile), ex);
            }
        }

        /// <summary>
        /// Write this instance to the given file.
        /// </summary>
        /// <param name="configFile">Fully qualified path name for configuration data file</param>
        /// <returns></returns>
        public void SaveAs(string configFile)
        {
            try
            {
                using (var tw = new XmlTextWriter(configFile, null))
                {
                    tw.Formatting = Formatting.Indented;
                    var serializer = new XmlSerializer(typeof(Configuration));
                    serializer.Serialize(tw, this);
                    tw.Flush();
                }
            }
            catch (Exception ex)
            {
                throw new ArgumentException(String.Format("Cannot save configuration data to {0}", configFile), ex);
            }
        }
    }
}
