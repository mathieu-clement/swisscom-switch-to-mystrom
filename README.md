# myStrom proxy for Swisscom Home Smart Switch

## What

This is a very minimal Flask web application that answers requests made by the Home Assistant integration for
myStrom smart switches by forwarding them to a Swisscom Home Smart Switch.

## Why

Swisscom Home Smart Switches normally require a Swisscom Internet-Box and the Android/iOS Swisscom Home App
to function. Maybe this is why they're twice as cheap as a myStrom Wi-Fi Switch (they also lack a temperature
and electric current sensor).

The API for Swisscom Switches seems to be -- for the most part -- identical to that of myStrom: https://api.mystrom.ch/

## Configuration

### Smart Switch

1. Press and hold the button on the side of the switch and plug it into an outlet until the red light starts flashing.
The switch is now in Access Point mode.
2. From your _computer_, connect to the "Switch-XXYYZZ" Wi-Fi network and verify that you can browse http://192.168.254.1
3. Set your Wi-Fi SSID and password:

```bash
curl --location --request POST '192.168.254.1/api/v1/connect' \                                                                 
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data-raw '{
    "ssid": "your_wifi_network_name", "passwd": "your_wifi_password"
  }'
```

You can also assign a fixed IP address, gateway, subnet, etc. Refer to the myStrom API.
I personally configure my DHCP server to assign a static IP address to my smart home devices (most routers
allow you to do this, sometimes you need to log in to your ISP account online to do so).

4. The switch will now reboot and connect to your network. Switch your computer back to your home Wi-Fi / Ethernet / etc.
5. Find it on your network, and get the "report": `curl --location '192.168.0.25/report'`

### Docker

We assume everything will be running inside Docker on the same machine:

  - Home Assistant (HA)
  - This application

This presents a few challenges:

  - The HA integration for myStrom only supports the default HTTP port (80) for the myStrom device.
    The workaround we'll use is to create a private Docker network between the proxy and HA, so
    that this application can run on port 80 without interfering with the host port 80.
  - Using a private docker network is incompatible with the "Host" network mode Home Assistant 
    normally uses in a Docker installation, so you will have to make sure to _expose_ port 8123
    (TCP) from HA and set it to "Bridge" mode.
  - When using "Bridge" mode, the container loses the ability to make/receive mDNS requests.
    Those are used to support the HomeKit integration in HA among other things.
    I have not explored this solution, but a container such as _mdns-repeater_ running in host mode
    and bridging the HA instance with the host network should be able to fill this gap.

Create an internal Docker network:

```docker network create <network>```

Replace `<network>` with a meaningful name for the network.

In my experience, for example with Unraid, the network will be persisted after reboot of the host.

You'll probably want to set the _subnet_ and _ip-range_. In this example the subnet is `172.20.0.0/24`. The proxy will use
`172.20.0.10` and the smart switch is reachable at `192.168.0.25`.

### Proxy

This application, which acts as a proxy, you will start with Docker in "Bridge" mode (because it needs to access 
the smart switch on the host network), and similarly to HA you should connect it to the private Docker
network after it boots up:

```docker network connect --ip 172.20.0.10 <network> <container>```

The image is available in the `mathieuclement/swisscom-switch-to-mystrom` repository on Docker Hub. You can use the
`latest` tag. The image is currently built for the `linux/amd64` platform.

Set the following environment variables:

  - `REAL_HOST`: the IP address of the real physical device on the host network (`192.168.0.25` in my example above)
  - `LISTEN_HOST`: the IP address of the proxy instant on the Docker internal network (`172.20.0.10` in my example)
  - `LISTEN_PORT`: the port the web application will use. Normally this is port `80`. **You do NOT need to expose this port.**

Don't forget to set the container to auto-start.

### Home Assistant Configuration

Add your switch to the _configuration.yaml_ file:

```yaml
switch:
  - platform: mystrom
    host: 172.20.0.10
    name: Living Room Floor Lamp
```

If running Home Assistant in Docker, you will have to use the "Bridge" network, so that you can connect to the
private Docker network as well, and expose port 8123 (TCP). After launching your HA container, issue the following command:

```docker network connect --ip 172.20.0.11 <network> <container>```

Replace `<network>` with the same name as earlier, and `<container>` with the container name. Yes you should assign
a name to your container, but you don't have to.

In a system such as Unraid, you can set this as a post-argument (preceded by `&& `) in the advanced view of the container.

Try to start HA after the proxy, or you might see the switch entity is "unavailable" until it gets online.

## Limitations

You will probably lose the HomeKit integration and any other that rely on mDNS. Refer to the "challenges" above
for a possible workaround.
