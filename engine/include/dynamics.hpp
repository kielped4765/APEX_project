#pragma once
#include "aircraft.hpp"
#include <cmath>

struct FlightControls {      // defining the autopilot control inputs
    double throttle;        // 0.0-1.0
    double elevator;       // -1.0-1.0
    double aileron;        // -1.0-1.0
    double rudder;         // -1.0-1.0
};

class FlightDynamics {
    public:
        explicit FlightDynamics(double dt_s = 0.02);           // sets time step to .02 seconds to correspond to 50 Hz
        AircraftState step(const AircraftState& current,        // Main function called every tick to advance the aircraft physics forward
                           const FlightControls& controls);     

    private:
        double dt_;
        AircraftState compute_derivatives(const AircraftState& s,                   // represents rate of change of the variable
                                          const FlightControls& c) const;
        static AircraftState add_scaled(const AircraftState& s,
                                        const AircraftState& k, double scale);
        static constexpr double MASS_KG          = 8000.0;                         // Hardcoded physical parameters defining the simulated aircrafts aerodynamic profile
        static constexpr double WING_AREA_M2     = 30.0;
        static constexpr double MAX_THRUST_N     = 60000.0;
        static constexpr double CL_ALPHA         = 5.0;
        static constexpr double CD0              = 0.04;
        static constexpr double K_INDUCED        = 0.04;
        static constexpr double AIR_DENSITY      = 1.225;
        static constexpr double GRAVITY          = 9.81;
};