# Onboard CAN Deserializer

A C++ program that works in tandem with a Python program and a Redis DB to deserialize and stream live CANbus data for the IC and EV.

## Building
This project uses CMake to build.

```sh
mkdir build
cd build
cmake ..
cmake --build .
```

## Running
After building, if you're in onboard-can-deserializer/build/, you can simply run with:
```sh
./onboard-can-deserializer
```


