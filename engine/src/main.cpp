#include <iostream>
#include <thread> 
#include <chrono>
#include <cstring>
#include "engine/include/frame.hpp"

int main() {
    
    std::cout << "[APEX engine] Starting simulation...";

    uint32_t sequence_id = 0;                                               // Keeping track starting
    // at 0 of how many frames have been generated
    const int tick_rate_hz = 50;                                            // Keeping target
    // simulation frequency at 50 Hz
    const auto interval = std::chrono::milliseconds(1000 / tick_rate_hz);   // Calculating
    // how long program needs to wait between loops

    for (int i = 0; i < 100; ++i) {     // Looping 100 times to generate 100 telemetry frames
        apex::TelemetryFrame frame;

        frame.sequence_id = ++sequence;

        frame.timestamp_ms = std::chrono::duration_cast<std::chrono::milliseconds>(     // Converts to milliseconds
            std::chrono::system_clock::now().time_since_epoch()
        ).count();

        frame.vehicle_speed = 120.5f + (i * 0.1f);
        frame.engine_temperature = 90.0f;                   // setting values for each variable
        frame.fuel_load_kg = 50.0f - (i * 0.05f);
        frame.vertical_energy = 1.2f;

        std::strncpy(frame.car_id, "APEX-01", sizeof(frame.car_id));    // setting setting the car identifier into fixed-size

        std::cout << "Seq: " << frame.sequence_id                   // outputting the frame metrics for visual verification
                  << " | Speed: " << frame.vehicle_speed << "km/h"
                  << " | Fuel: " << frame.fuel_load_kg << "kg"
                  << " | Size: " << sizeof(frame) << " bytes\n";

        std::this_thread::sleep_for(interval);    // Pausing the loop for the calculated interval

    }

    std::cout << "[APEX engine] Simulation completed.\n";

    return 0;
}