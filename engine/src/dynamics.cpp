#include "dynamics.hpp"

FlightDynamics::FlightDynamics(double dt_s) : dt_(dt_s) {}      // Takes dt_s (time step value) defaulting to 0.02 seconds for 50 Hz staying consistant

AircraftState FlightDynamics::step(const AircraftState& s,      // Accepts the current aircraft state (s) and pilot controls (c) and returns calculated next state
                                   const FlightControls& c) {
    auto k1 = compute_derivatives(s,                      c);    // Calculating rate of change of slope
    auto k2 = compute_derivatives(add_scaled(s, k1, dt_/2), c);  // Evaluates slope halfway through
    auto k3 = compute_derivatives(add_scaled(s, k2, dt_/2), c);  // Re-evaluates slope halfway through time step
    auto k4 = compute_derivatives(add_scaled(s, k3, dt_), c);    // Evaluates slope at full end of time step
    
    auto W = [&](double a, double b, double c2, double d) {     // A C++ lambda function that implements the Runge-Kutta weighted average formula: it combines all four slopes
        return (dt_/6.0)*(a + 2.0*b + 2.0*c2 + d); };

    AircraftState next = s;         // Calcuating next state for each category k1-k4
    next.altitude_m    += W(k1.altitude_m,    k2.altitude_m,    k3.altitude_m,    k4.altitude_m);   
    next.airspeed_mps  += W(k1.airspeed_mps,  k2.airspeed_mps,  k3.airspeed_mps,  k4.airspeed_mps);
    next.vertical_speed+= W(k1.vertical_speed,k2.vertical_speed,k3.vertical_speed,k4.vertical_speed);
    next.pitch_rad     += W(k1.pitch_rad,     k2.pitch_rad,     k3.pitch_rad,     k4.pitch_rad);
    next.roll_rad      += W(k1.roll_rad,      k2.roll_rad,      k3.roll_rad,      k4.roll_rad);
    next.yaw_rad       += W(k1.yaw_rad,       k2.yaw_rad,       k3.yaw_rad,       k4.yaw_rad);
    next.pitch_rate    += W(k1.pitch_rate,    k2.pitch_rate,    k3.pitch_rate,    k4.pitch_rate);
    next.roll_rate     += W(k1.roll_rate,     k2.roll_rate,     k3.roll_rate,     k4.roll_rate);
 
    next.thrust_n       = c.throttle * MAX_THRUST_N;
    next.engine_rpm     = c.throttle * 10000.0;
    next.fuel_flow_kgps = next.thrust_n * 2.0e-5;
    next.fuel_mass_kg   = std::max(0.0, s.fuel_mass_kg - next.fuel_flow_kgps * dt_);
    next.alpha_rad      = std::atan2(next.vertical_speed, next.airspeed_mps + 1e-6);
    next.sequence_num   = s.sequence_num + 1;
    next.sim_time_s     = s.sim_time_s + dt_;
    return next;
}

AircraftState FlightDynamics::compute_derivatives(      // Empty state struct filled with zeros to store calculated rates of change
        const AircraftState& s, const FlightControls& c) const {
    AircraftState d{};  // zero-initialize
    double q    = 0.5 * AIR_DENSITY * s.airspeed_mps * s.airspeed_mps;
    double CL   = CL_ALPHA * s.alpha_rad + 0.3 * c.elevator;
    double CD   = CD0 + K_INDUCED * CL * CL;
    double lift = q * WING_AREA_M2 * CL;
    double drag = q * WING_AREA_M2 * CD;
    d.airspeed_mps   = (c.throttle * MAX_THRUST_N - drag) / MASS_KG;
    d.vertical_speed = (lift - MASS_KG * GRAVITY) / MASS_KG;
    d.altitude_m     = s.vertical_speed;
    d.pitch_rate     = c.elevator * 1.5 - s.pitch_rate * 0.3;
    d.pitch_rad      = s.pitch_rate;
    d.roll_rate      = c.aileron  * 2.0 - s.roll_rate  * 0.4;
    d.roll_rad       = s.roll_rate;
    d.yaw_rad        = c.rudder   * 0.5;
    return d;
}
 
AircraftState FlightDynamics::add_scaled(       // A helper utility required by RK4 to combine a base state (s) with a derivative rate (k) multiplied by a fractional time scale
        const AircraftState& s, const AircraftState& k, double sc) {
    AircraftState r = s;
    r.altitude_m    += k.altitude_m    * sc;
    r.airspeed_mps  += k.airspeed_mps  * sc;
    r.vertical_speed+= k.vertical_speed* sc;
    r.pitch_rad     += k.pitch_rad     * sc;
    r.roll_rad      += k.roll_rad      * sc;
    r.yaw_rad       += k.yaw_rad       * sc;
    r.pitch_rate    += k.pitch_rate    * sc;
    r.roll_rate     += k.roll_rate     * sc;
    return r;
}