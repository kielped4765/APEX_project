#pragma once
#include <cstdint>

struct AircraftState{

    // Position of earth
    double altitude_m;
    double latitude_deg;
    double longitude_deg;

    // Velocity
    double airspeed_mps;
    double vertical_speed;
    double ground_speed_mps;

    // Attitude  (angles)
    double pitch_rad;
    double roll_rad;
    double yaw_rad;

    // Angular rates
    double pitch_rate;
    double roll_rate;
    double yaw_rate;
    
    // Engine
    double engine_rpm;
    double thrust_n;
    double fuel_flow_kgps;
    double fuel_mass_kg;

    // Loads
    double g_load;
    double alpha_rad;

    // Timing
    uint64_t sequence_num;
    double sim_time_s;
    
};
