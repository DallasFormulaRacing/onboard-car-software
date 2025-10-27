
#include <CanDriver.hpp>

#include <CanId.hpp>

#include <CanMessage.hpp>

#include <CanException.hpp>
#include <CanInitException.hpp>
#include <CanCloseException.hpp>

#include <iostream>
#include <unistd.h>
using namespace std::chrono_literals;


using sockcanpp::CanDriver;
using sockcanpp::CanMessage;
using sockcanpp::filtermap_t;
// using sockcanpp::exceptions::CanException;

void receiveFrame(CanDriver& driver);
void handleErrorFrame(const CanMessage& msg);

int main() {

    CanDriver cDriver{"vcan0", CAN_RAW}; // No default sender ID


    cDriver.setErrorFilter(); // Receive error frames

    filtermap_t canFilters{
        { 0x489,    0x7ff } // filter messages with 0x489 as ID
    };
    cDriver.setCanFilters(canFilters); // Set X amount of CAN filters. See https://docs.kernel.org/networking/can.html#raw-protocol-sockets-with-can-filters-sock-raw
    cDriver.setCollectTelemetry(); // Enable telemetry collection, such as timestamps, data sent, etc.
    cDriver.setReceiveOwnMessages(); // Echo sent frames back
    cDriver.setReturnRelativeTimestamps(); // Enable relative timestamps

    std::cout << "Waiting for CAN frames - send a can msg starting with 489!" << std::endl;

    // Print out incoming CAN msgs forever
    while (true) {
        receiveFrame(cDriver);
    }

}

void receiveFrame(CanDriver& driver) {
    if (!driver.waitForMessages(0ns)) { return; } // No messages in buffer

    const auto receivedMsg = driver.readMessage();
    std::cout << receivedMsg << std::endl; // Outputs: CanMessage(canId: XXX, data: FF FF FF FF, timestampOffset: Nms)

    if (receivedMsg.isErrorFrame()) {
        handleErrorFrame(receivedMsg);

    }
}

void handleErrorFrame(const CanMessage& msg) {
    std::cerr << "Received an error frame! :(" <<  msg << std::endl;
}
