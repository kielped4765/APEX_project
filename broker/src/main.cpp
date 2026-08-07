#include "aircraft.hpp"
#include "crypto.hpp"
#include "ring_buffer.hpp"
#include "attacker.hpp"
#include "frame.hpp"
#include <iostream>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <chrono>

int connect_to_monitor(const char* path) {
    int fd = socket(AF_UNIX, SOCK_STREAM, 0); // Create a UNIX domain socket for communication with the monitor
    sockaddr_un addr{};
    addr.sun_family = AF_UNIX; // Set the address family to AF_UNIX for UNIX domain sockets
    strncpy(addr.sun_path, path, sizeof(addr.sun_path) -1); // Copy the provided path to the socket address structure, ensuring not to exceed the maximum path length
    while (connect(fd, (sockaddr*)&addr, sizeof(addr)) < 0) {
        std::cout << "[BROKER] Waiting for monitor to start...\n"; // If the connection fails, print a message indicating that the broker is waiting for the monitor to start
        sleep(1); // Sleep for 1 second before retrying the connection
    }
    return fd; // Return the file descriptor for the connected socket
}

int main() {
    SharedRingBuffer* ring = open_shared_ring("apex_ring_buffer"); // Open the shared ring buffer for communication with the telemetry source
    TelemetryCrypto   crypto("keys/aes.key", "keys/hmac.key");     // Loads the secret keys from disk files
    AttackInjector    injector(0.05);                              // Initializes the attack injector with a 5% attack probability rate                              
    int               sock = connect_to_monitor("/tmp/apex_telemetry.sock");    // Connects to the Python monitor socket file
    TelemetryFrame    frame{}, prev{};                              // Instantiates current and previous tracking telemetry frame structures

    while (true) {
        AircraftState state;                                        // Declares a local variable to hold raw aircraft state data.
        if (!ring_pop(*ring, state)) continue;                      // Pulls the next state from the shared ring buffer; skips the iteration if the buffer is empty

        frame.magic         = FRAME_MAGIC;                          // Sets the frame magic header to identify valid APEX telemetry packets
        frame.frame_type    = FrameType::TELEMETRY;                 // Marks the frame type as standard telemetry
        frame.attack_label  = AttackType::NONE;                     // Default sets the ground-truth attack label to none
        frame.sequence_num  = state.sequence_num;                   // Copies the monotonic sequence number from the flight state
        frame.timestamp_us  = std::chrono::duration_cast<std::chrono::microseconds>(    // Generates the current system epoch timestamp in microseconds
            std::chrono::system_clock::now().time_since_epoch()).count();               

        auto ct = crypto.encrypt(                                                       // Encrypts the raw aircraft state payload and generates a fresh random IV
            reinterpret_cast<const uint8_t*>(&state), sizeof(state), frame.iv);         
        memcpy(frame.payload, ct.data(),                                                // Copies the resulting ciphertext into the frame's payload buffer
               std::min(ct.size(), sizeof(frame.payload)));                             

        frame.attack_label = injector.maybe_inject(frame, prev);                        // Conditionally applies a simulated cyberattack based on the injection rate

        // Sign things before the hmac field
        auto mac = crypto.hmac_sign(                                                    // Computes the cryptographic HMAC-SHA256 signature for the frame
            reinterpret_cast<const uint8_t*>(&frame),                                   
            sizeof(frame) - HMAC_SIZE);
        memcpy(frame.hmac, mac.data(), HMAC_SIZE);                                      // Copies the generated HMAC signature into the end of the frame struct

        send(sock, &frame, sizeof(frame), 0);                                           // Transmits the fully assembled, authenticated frame over the UNIX socket to the monitor
        prev = frame;       
    }
}