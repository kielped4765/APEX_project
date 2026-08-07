#include "attacker.hpp"
#include "aircraft.hpp"
#include <chrono>
#include <cstring>

AttackInjector::AttackInjector(double rate)
    : rng_(std::chrono::steady_clock::now().time_since_epoch().count()), rate_(rate) {}     // Constructor to initialize the attack injector with a specified attack rate (default is 5%)

AttackType AttackInjector::maybe_inject(TelemetryFrame& f,
                                        const TelemetryFrame& prev) {
    if (roll_(rng_) >= rate_) { last_valid_=f; has_prev_=true; return AttackType::NONE; }  // If the random roll is greater than or equal to the attack rate, store the current frame as the last valid frame and return NONE (no attack injected)
    switch (type_(rng_)) {
        case 0: inject_spoof(f);    return AttackType::SPOOF;       // If the random type is 0, inject a spoof attack into the frame and return SPOOF
        case 1: inject_replay(f);   return AttackType::REPLAY;      // If the random type is 1, inject a replay attack into the frame and return REPLAY
        case 2: inject_corrupt(f);  return AttackType::CORRUPT;     // If the random type is 2, inject a corrupt attack into the frame and return CORRUPT
        case 3: inject_drift(f);    return AttackType::DRIFT;       // If the random type is 3, inject a drift attack into the frame and return DRIFT
    }
}

// SPOOF: impossible sensor values - tests physics rules
void AttackInjector::inject_spoof(TelemetryFrame& f) {
    AircraftState fake{};
    fake.altitude_m     = -500.0;   // below sea level
    fake.airspeed_mps   =  600.0;   // above max airspeed
    fake.thrust_n       =    0.0;   // engine is nonexistent
    fake.vertical_speed =   50.0;   // climbing with no thrust
    fake.g_load         =   15.0;   // beyond structural limits
    memcpy(f.payload, &fake, std::min(sizeof(fake), sizeof(f.payload))); // Copy the fake aircraft state into the payload of the telemetry frame, ensuring not to exceed the payload size
    f.attack_label = AttackType::SPOOF; // Set the attack label of the telemetry frame to SPOOF 
}

// REPLAY: valid HMAC, duplicate sequence - tests seq check
void AttackInjector::inject_replay(TelemetryFrame& f) {    // Method to inject a replay attack into a telemetry frame by replacing its payload with that of the last valid frame
    if (!has_prev_) return;                                // If there is no previous valid frame, return without injecting a replay attack
    f = last_valid_;                                       // Replace the current telemetry frame with the last valid frame, effectively replaying the previous frame
    f.attack_label = AttackType::REPLAY;                   // Set the attack label of the telemetry frame to REPLAY
}

// Corrupt: if one bit flips - HMAC will fail
void AttackInjector::inject_corrupt(TelemetryFrame& f) {     // Method to inject a drift attack into a telemetry frame by gradually modifying its payload data over time
    size_t i = rng_() % PAYLOAD_SIZE;
    f.payload[i] ^= (uint8_t)(1u << (rng_() % 8));         // Randomly select a byte in the payload and flip a random bit within that byte to simulate a drift attack
    f.attack_label = AttackType::CORRUPT;                  // Set the attack label of the telemetry frame to CORRUPT
}

void AttackInjector::inject_drift(TelemetryFrame& f) {
    AircraftState s;                                       // Create an instance of AircraftState to hold the current state of the aircraft
    memcpy(&s, f.payload, std::min(sizeof(s), sizeof(f.payload))); // Copy the current payload of the telemetry frame into the AircraftState instance, ensuring not to exceed the size of the payload
    drift_offset_ += 10.0;                                       // Increment the drift offset by 10.0 to simulate gradual drift over time
    s.altitude_m  += drift_offset_;                                       // Modify the altitude of the aircraft state by adding the drift offset to simulate a drift attack
    memcpy(f.payload, &s, std::min(sizeof(s), sizeof(f.payload))); // Copy the modified AircraftState back into the payload of the telemetry frame, ensuring not to exceed the size of the payload
    f.attack_label = AttackType::DRIFT;                   // Set the attack label of the telemetry frame to DRIFT
}
