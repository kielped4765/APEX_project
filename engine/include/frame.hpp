#pragma once                        // Only included during compilation

#include <cstdint>                  // imports standard fixed-width integer types
#include <array>                    // imports the array library

namespace apex {                    // wraps code in apex
    #pragma pack(push, 1)           // packing structure tightly    
    struct TelemetryFrame {         // defines a structure for telemetry data
        uint32_t sequence_id;       // A 4-byte identifer for the telemetry frame
        uint64_t timestamp_ms;      // A 8-byte timestamp in milliseconds
        float vehicle_speed;        // A 4-byte float representing the vehicle speed
        float engine_temperature;   // A 4-byte float representing the engine temperature
        float fuel_load_kg;         // A 4-byte float representing the fuel load in kilograms
        float vertical_energy;      // A 4-byte float representing the vertical energy
        char car_id[8];             // A 8-byte character array for the car identifier
    };
    #pragma pack(pop)

    } 