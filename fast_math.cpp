#include <pybind11/pybind11.h>

namespace py = pybind11;

// A high-speed function to calculate a baseline risk score 
// based on transaction amount and the user's daily velocity.
double calculate_velocity_risk(double amount, int daily_transactions) {
    double risk_score = 0.0;
    
    if (amount > 10000.0) risk_score += 0.5;
    if (daily_transactions > 15) risk_score += 0.3;
    
    // Cap the risk score at 1.0 (100% risk)
    return (risk_score > 1.0) ? 1.0 : risk_score;
}

// This macro binds the C++ function so Python can import it
PYBIND11_MODULE(fast_math, m) {
    m.doc() = "C++ High Performance Math Module for MAZI"; 
    m.def("calculate_velocity_risk", &calculate_velocity_risk, "Calculates risk based on velocity");
}