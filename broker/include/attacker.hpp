#pragma once
#include "frame.hpp"
#include <random>

class AttackInjector {                                          // Class to inject attacks into telemetry frames for testing and training purposes
public:                                                         // Public interface for the AttackInjector class
    explicit AttackInjector(double attack_rate = 0.05);         // Constructor to initialize the attack injector with a specified attack rate (default is 5%)
    AttackType maybe_inject(TelemetryFrame& frame,              // Method to potentially inject an attack into a telemetry frame based on the specified attack rate and the previous valid frame
                            const TelemetryFrame& prev_valid);  // Returns the type of attack injected (if any) or NONE if no attack was injected

private:                                                        // Private member variables for the AttackInjector class
        std::mt19937 rng_;                                      // Random number generator for attack injection
        std::uniform_real_distribution<double> roll_{0.0, 1.0}; // Uniform distribution to determine whether to inject an attack based on the attack rate
        std::uniform_int_distribution<int>     type_{0, 3};     // Uniform distribution to randomly select the type of attack to inject (SPOOF, REPLAY, CORRUPT, DRIFT)
        double rate_;                                           // Attack rate for determining the likelihood of injecting an attack into a telemetry frame
        TelemetryFrame last_valid_;                             // Stores the last valid telemetry frame for potential use in attack injection
        bool has_prev_{false};                                  // Flag to indicate whether there is a previous valid telemetry frame available for attack injection
        double drift_offset_{0.0};                              // Offset value for simulating drift attacks by modifying the payload of telemetry frames

        void inject_spoof(TelemetryFrame& f);                   // Method to inject a spoof attack into a telemetry frame by modifying its payload
        void inject_replay(TelemetryFrame& f);                  // Method to inject a replay attack into a telemetry frame by replacing its payload with that of the last valid frame
        void inject_corrupt(TelemetryFrame& f);                 // Method to inject a corrupt attack into a telemetry frame by randomly altering its payload data
        void inject_drift(TelemetryFrame& f);                   // Method to inject a drift attack into a telemetry frame by gradually modifying its payload data over time
        
};