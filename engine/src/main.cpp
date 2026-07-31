#include <iostream>
#include <chrono>
#include <thread>
#include "aircraft.hpp"
#include "dynamics.hpp"
#include "ring_buffer.hpp"

int main() {                                                            // Calls our shared memory creation function to set up physical RAM ring buffer
    SharedRingBuffer* ring = create_shared_ring("apex_ring_buffer");
    std::cout << "[ENGINE] Shared memory ready. 50 Hz loop starting.\n";

    AircraftState state{};              // zero-initalizes all variables
    state.altitude_m    = 3000.0;       
    state.airspeed_mps  = 120.0;
    state.thrust_n      = 30000.0;
    state.fuel_mass_kg  = 2000.0;
    state.g_load        = 1.0;
    state.sequence_num  = 0;
    state.sim_time_s    = 0.0;

    FlightControls controls{};          // creates a default controls object and sets throttle to 50%
    controls.throttle = 0.5;

    FlightDynamics dynamics(0.02);      // instantiates our physical engine passing 0.02 seconds as the time step

    using namespace std::chrono;        // bringing in the namespace into scope to write cleaner time-related code
    auto next_tick = steady_clock::now();   // captures current high-resolution monotonic clock time for baseline for loop timing
    const auto TICK = milliseconds(20);

    while (true) {                          // defines a constant duration of 20 milliseconds, which represents one tick of a 50 Hz frequency
        state = dynamics.step(state, controls); // Runs the Rk4 physics equations for the current frame
        ring_push(*ring, state);                // Pushes newly calculated AircraftState into our lock-free shared memory

        if (state.sequence_num % 50 == 0)       // Check if current sequence number is a multiple of 50 
            std::printf("[ENGINE] t=%.1fs seq=%lu alt=%.0fm spd=%.1fm/s\n", // Prints a formatted status log to the console
                state.sim_time_s, state.sequence_num,
                state.altitude_m, state.airspeed_mps);

        next_tick += TICK;                      // Advances our target time marker by exactly 20 milliseconds for next loop iteration
        std::this_thread::sleep_until(next_tick);
    }
}