import requests
from bs4 import BeautifulSoup

"""
XfinityRouter Project
---------------------
This project was designed to control my home's Xfinity router using the HTTP
interface for the device. It currently can:
    - Login to the device
    - Retrieve the list of devices currently connected to the network
    - Add a port forwarding entry (open a port programmatically)
    - Enable/Disable port forwarding

Potential Uses
    - Build a history of connected devices. Pattern-finding algorithms can use this
      information to predict when a specific device will be on the network.
    - To extend the functionality of my HomeServer project. I can open network ports
      for a brief period of time so that I am more protected from outside attacks.
"""


def grabChunk(buffer: str, startStr: str, endStr: str):
    """Returns None or a chunk of text in buffer after startStr and before endStr."""
    if buffer.find(startStr) == -1:
        return None
    if buffer.find(endStr) == -1:
        return None

    startIndex = buffer.find(startStr) + len(startStr)
    endIndex = buffer[startIndex:].find(endStr) + startIndex
    return buffer[startIndex:endIndex]  # Should be text sandwiched between the 2 argument strings


class Router:
    """A class that interacts with an Xfinity router."""

    # Constant web paths
    addForwardForm = "/goform/port_forwarding_add"
    addForwardPage = "/port_forwarding_add.asp"
    portForwardingForm = "/goform/port_forwarding"
    portForwardingPath = "/port_forwarding.asp"
    loginForm = "/goform/home_loggedout"
    connectedDevicesPage = "/connected_devices_computers.asp"

    def __init__(self, ip="10.0.0.1", pwd="password", port=80):
        """Setup information for interacting with router through HTTP."""
        self.ip = ip
        self.pwd = pwd
        self.port = port
        self.session = requests.Session()

    def login(self):
        """Login to the router."""

        self.session.get("http://%s/" % self.ip)  # Get cookies
        load = {"loginUsername": "admin",
                "loginPassword": self.pwd}
        path = "http://%s%s" % (self.ip, self.loginForm)
        response = self.session.post(path, data=load)
        if response.status_code == 200:
            return True
        else:
            print('Status code: %d' % response.status_code)
            return False

    def getToken(self, path) -> str:
        """For port forwarding functions to grab the CSRF token for POST requests."""

        csrfStart = "csrf_token\" value=\""  # Start of csrf token hidden HTML input field
        csrfStop = "\""  # Closing quotation mark

        page = self.session.get("http://%s%s" % (self.ip, path)).text
        token = grabChunk(page, csrfStart, csrfStop)  # Extract our token
        return token

    def setPortForwarding(self, toggle: bool):
        """Sets the router port forwarding to either Enable or Disable.
        Requires the object to be logged in."""

        load = {'forwarding': 'Enabled' if toggle else 'Disabled',
                'csrf_token': self.getToken(self.portForwardingPath)}
        response = self.session.post('http://%s%s' % (self.ip, self.portForwardingForm), data=load)

        if response.status_code == 200:
            return True
        else:
            print('Set port forwarding: Status code: %d' % response.status_code)
            return False

    def addPortForward(self, serviceName: str, localAddress: int, port: int) -> bool:
        """Add a port forwarding entry to the router. This exposes a port to the internet."""

        load = {'storage_row': -1,
                'csrf_token': self.getToken(self.addForwardPage),
                'common_services': 'other',
                'other_service': serviceName,
                'service_type': 'tcp_udp',
                'server_ip_address_4': str(localAddress),
                'start_port': str(port),
                'end_port': str(port)}
        response = self.session.post('http://%s%s' % (self.ip, self.addForwardForm), data=load)

        if response.status_code == 200:
            return True
        else:
            print('Add forward: Status code: %d' % response.status_code)
            return False

    def getConnectedDevices(self) -> list:
        """Return a list of devices currently connected to this router."""
        # TODO Add code to retrieve connected devices
        response = self.session.get('http://%s%s' % (self.ip, self.connectedDevicesPage))

        if response.status_code != 200:  # Page failed to load
            return []


        # HTML Elements for device data:
        # <table class="data"
        # <tbody>
        # 2nd <tr> and on...

        parser = BeautifulSoup(response.content, 'html.parser')
        parser = parser('table', attrs={'class': 'data'})[0]
        devices = parser('tr')[1:]  # Tag list of device tr element

        deviceProperties = []
        for device in devices:
            name = grabChunk(device.text, "\n", "\n")
            ipv4 = grabChunk(device.text, "IPV4 Address\n", "\n")
            mac = grabChunk(device.text, "MAC Address\n", "\n")
            deviceProperties.append((name, ipv4, mac))
        return deviceProperties  # List of (name, ipv4, mac)


if __name__ == "__main__":
    r = Router(pwd="password")  # "password" is the default for Xfinity routers
    r.login()  # Login to the router via HTTP
    devices = r.getConnectedDevices()  # Retrieve currently-connected devices
