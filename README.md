# Onboard CAN Software

A telemetry pipeline for vehicle-mounted embedded systems.

## Containers

- **Deserializer**: Reads CAN bus data and stores it in Redis
- **Redis**: In-memory data store for telemetry buffering and persistence
- **Streamer**: Reads telemetry from Redis and streams to Kafka

## Build and Run

Build the project:
```bash
docker compose build
```

Run the application:
```bash
docker compose up
```

## Prerequisites

This application requires a CAN interface. For development/testing, you can use a virtual CAN interface (vcan0).

Run the following commands on the host machine:

Load the vcan kernel module:
```bash
modprobe vcan
```

Verify the module loaded successfully:
```bash
lsmod | grep vcan
```

Expected output:
```
vcan                   12288  0
```

