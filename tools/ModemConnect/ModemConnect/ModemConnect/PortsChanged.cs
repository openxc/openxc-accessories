using System;

namespace ModemConnect
{
    public enum EventType
    {
        Insertion,
        Removal,
    }

    public class PortsChangedArgs : EventArgs
    {
        private readonly EventType m_EventType;

        private readonly string[] m_SerialPorts;

        public PortsChangedArgs(EventType eventType, string[] serialPorts)
        {
            m_EventType = eventType;
            m_SerialPorts = serialPorts;
        }

        public string[] SerialPorts
        {
            get
            {
                return m_SerialPorts;
            }
        }

        public EventType EventType
        {
            get
            {
                return m_EventType;
            }
        }
    }
}
