using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.RegularExpressions;
using System.Windows.Forms;
using log4net;
using log4net.Config;

namespace ModemConnect
{
    public partial class Form1 : Form
    {
        private TerminalProcess m_TerminalProcess;
        private string m_SelectedSerialPort = String.Empty;

        private static readonly ILog _Logger = LogManager.GetLogger(typeof(Form1));
        private Configuration m_Config;

        public Form1()
        {
            m_Config = Configuration.GetInstance();

            BasicConfigurator.Configure();

            InitializeComponent();
            errorLabel.Text = "";

            var connectedModemPorts = FilterPorts(SerialPortService.GetAvailableSerialPorts());
            SetSerialPortsList(connectedModemPorts);
            HandleSerialPortsChange(connectedModemPorts);

            SerialPortService.PortsChanged += SerialPortServicePortsChanged;

            if (!File.Exists(m_Config.TerminalApplicationPath))
            {
                MessageBox.Show(
                    "The terminal application specified in the configuration file was not found.  This application will not be able to automatically open the terminal when the modem is connected.\n\nTo resolve, either:\na) install TeraTerm (see installation directory for install file) or\nb) update the configuration file.",
                    "OpenXC Modem Connect", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
        }

        private void SerialPortServicePortsChanged(object sender, PortsChangedArgs args)
        {
            comPortsListBox.Invoke(new Action(() =>
                                                  {
                                                      var connectedModemPorts = FilterPorts(args.SerialPorts);
                                                      SetSerialPortsList(connectedModemPorts);
                                                      HandleSerialPortsChange(connectedModemPorts);
                                                  }));
        }

        private void OnTerminalProcessTerminated(object sender, EventArgs eventArgs)
        {
            m_TerminalProcess = null;

            var message = "Terminal application exited.";
            _Logger.Info(message);
            errorLabel.Invoke(new Action(() => { errorLabel.Text = message; }));
        }

        private string[] FilterPorts(string[] serialPorts)
        {
            var openXCPorts = OpenXCPortNames.GetOpenXCPorts(m_Config.VID, m_Config.PID);
            var connectedOpenXCPorts = openXCPorts.Intersect(serialPorts).ToArray();
            return connectedOpenXCPorts;
        }

        private void HandleSerialPortsChange(string[] serialPorts)
        {
            // Are we connected to a port that went away?
            if ((m_TerminalProcess != null) && (!serialPorts.Contains(m_SelectedSerialPort)))
            {
                _Logger.Info("Serial port " + m_SelectedSerialPort + " disconnected.  Closing Terminal Application.");
                m_TerminalProcess.Disconnect();
                m_TerminalProcess = null;
                errorLabel.Text = "Modem disconnected; terminal application closed.";
            }

            // Don't connect if already connected and unless the user requests it.
            if ((m_TerminalProcess == null) && autoConnectCheckBox.Checked && (serialPorts.Length == 1))
            {
                m_TerminalProcess = new TerminalProcess();
                m_TerminalProcess.ProcessTerminated += OnTerminalProcessTerminated;
                m_SelectedSerialPort = serialPorts[0];

                var comPortNumber = Convert.ToInt32(Regex.Replace(m_SelectedSerialPort, "[^0-9]", "")).ToString();

                if (!String.IsNullOrEmpty(m_Config.PortNumber))
                {
                    comPortNumber = m_Config.PortNumber;
                }

                string arguments = m_Config.PortOption + m_Config.PortPrefix + comPortNumber;
                arguments += " " + m_Config.BaudRateOption + m_Config.BaudRate;
                arguments += " " + m_Config.ExtraArgs;

                if (!m_TerminalProcess.Connect(m_Config.TerminalApplicationPath, arguments))
                {
                    errorLabel.Text = "Error: Unable to launch: " + m_Config.TerminalApplicationPath;
                }
                else
                {
                    errorLabel.Text = "Connected to terminal application.  You may need to press ENTER there.";
                }
            }
        }

        private void SetSerialPortsList(string[] serialPorts)
        {
            var listString = (serialPorts.Length != 0) ? string.Empty : "(none)";
            
            comPortsListBox.Items.Clear();
            foreach (var connectedPort in serialPorts)
            {
                listString += connectedPort + " ";
                comPortsListBox.Items.Add(connectedPort);
            }

            _Logger.Info("OpenXC Modem(s) connected to serial port(s): " + listString);

            if (serialPorts.Length == 0)
            {
                comPortsListBox.Items.Add("(no modems detected)");
            }
        }

        private void OnFormClosing(object sender, FormClosingEventArgs e)
        {
            _Logger.Info("Application closing.");

            SerialPortService.CleanUp();

            if (m_TerminalProcess != null)
            {
                m_TerminalProcess.Disconnect();
                m_TerminalProcess = null;
            }
        }

        private void aboutToolStripMenuItem_Click(object sender, EventArgs e)
        {
            var aboutBox = new AboutBox();
            aboutBox.ShowDialog();
        }

        private void configToolStripMenuItem_Click(object sender, EventArgs e)
        {
            Process.Start("notepad.exe", Configuration.GetConfigFileName());
        }

    }
}
