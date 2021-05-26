# Mi Temp BLE Gateway

This is a small agent, publishing Mi Temp 2 telemetry to a [Drogue IoT](https://drogue.io) instance.

## Installing

* Install Podman

  * Fedora:
    ~~~shell
    sudo dnf -y install podman
    ~~~

  * Ubuntu 20.10 (including Raspberry Pi 3/4):
    ~~~shell
    sudo apt -y install podman runc
    ~~~

* Running it once

  podman run -net=host --privileged --rm -ti -e APP_ID=my-app -e DEVICE_ID=mitemp-gateway -e DEVICE_PASSWORD=device12 -e ENDPOINT=https://http-endpoint-drogue-iot.apps.your.cluster.tld -d ghcr.io/ctron/mitemp-gateway:latest

* Create a systemd unit (`/etc/systemd/system/mitemp-gateway.service`):

  ~~~ini
  [Unit]
  Description=MiTemp Gateway
  
  [Service]
  Restart=on-failure
  ExecStartPre=/usr/bin/rm -f /%t/%n-pid /%t/%n-cid
  ExecStart=/usr/bin/podman run --rm --conmon-pidfile /%t/%n-pid --cidfile /%t/%n-cid -net=host --privileged -e APP_ID=my-app -e DEVICE_ID=mitemp-gateway -e DEVICE_PASSWORD=device12 -e ENDPOINT=https://http-endpoint-drogue-iot.apps.your.cluster.tld -d ghcr.io/ctron/mitemp-gateway:latest
  ExecStop=/usr/bin/sh -c "/usr/bin/podman rm -f `cat /%t/%n-cid`"
  KillMode=none
  Type=forking
  PIDFile=/%t/%n-pid
  
  [Install]
  WantedBy=multi-user.target
  ~~~

  Be sure to replace the environment variables:

    * `ENDPOINT` – HTTP endpoint in Drogue Cloud
    * `APP_ID` – Application ID in Drogue Cloud
    * `DEVICE_ID` – (Gateway) Device ID in Drogue Cloud (defaults to `mitemp-gateway` in this readme)
    * `DEVICE_PASSWORD` – Password part of the device credentials

* Reload the daemon:

  ~~~shell
  sudo systemctl daemon-reload
  ~~~

* Activate the unit

  ~~~shell
  sudo systemctl enable --now mitemp-gateway.service
  ~~~

* Ensure to create one device per sensor, and a gateway in Drogue Cloud

    * Create a gateway
      
      ~~~
      drg create device --app my-app mitemp-gateway-ctron --spec '{
        "credentials":{
          "credentials":[
            {"pass": "my-secret-password"}
          ]
        }
      }'
      ~~~

    * Create a device per sensor, using the Bluetooth MAC
    
      ~~~
      drg create device --app my-app <sensor> --spec '{
        "gatewaySelector": {
          "matchNames": [
            "mitemp-gateway-ctron"
          ]
        }
      }'
      ~~~
