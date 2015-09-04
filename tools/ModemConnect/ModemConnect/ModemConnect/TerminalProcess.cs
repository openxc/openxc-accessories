using System;
using System.Diagnostics;
using log4net;

namespace ModemConnect
{
    internal class TerminalProcess
    {
        private Process m_MyProcess;
        private bool m_IsStarted;
        
        public event EventHandler<EventArgs> ProcessTerminated;

        private static readonly ILog _Logger = LogManager.GetLogger(typeof(TerminalProcess));

        public bool Connect(string applicationPath, string arguments)
        {
            // Start a process to print a file and raise an event when done.
            if (m_MyProcess == null)
            {
                m_MyProcess = new Process
                                  {
                                      StartInfo = {FileName = applicationPath, Arguments = arguments},
                                      EnableRaisingEvents = true
                                  };
                m_MyProcess.Exited += TerminalProcessExited;
                try
                {
                    var isStarted = m_MyProcess.Start();
                    if (isStarted)
                    {
                        _Logger.Debug("Started terminal process: [" + applicationPath + "]");
                        m_IsStarted = true;
                    }
                    else
                    {
                        _Logger.Error("Unable to start terminal process: [" + applicationPath + "] with args [" + arguments + "]");
                    }
                }
                catch (Exception ex)
                {
                    _Logger.Error("An error occurred start process [" + applicationPath + "] with args [" + arguments + "]: " + ex.Message);
                }
            }
            else
            {
                _Logger.Warn("Connect() called with a process already started.");
            }

            return m_IsStarted;
        }

        public void Disconnect()
        {
            if (m_IsStarted)
            {
                m_MyProcess.Kill();
                m_IsStarted = false;
            }
        }

        // Handle Exited event and display process information. 
        private void TerminalProcessExited(object sender, EventArgs e)
        {
            if (ProcessTerminated != null)
            {
                ProcessTerminated(sender, new EventArgs());
            }
        }
    }
}
