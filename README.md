# XfinityRouter Interface

This project was designed to control my home's Xfinity router using the HTTP interface for the device. It currently can:
  - Login to the device
  - Retrieve the list of devices currently connected to the network
  - Add a port forwarding entry (open a port programmatically)
  - Enable/Disable port forwarding

Potential Uses
  - Build a history of connected devices. Pattern-finding algorithms can use this information to predict when a specific device will be on the network.
  - Intruder detection system (IDS) for any wifi that uses an Xfinity router.
  - To extend the functionality of my HomeServer project. I can open network ports for a brief period of time so that I am more protected from outside attacks.

