#include <pybind11/pybind11.h>
#include <vector>
#include <cmath>

namespace py = pybind11;

double calculate_risk_score(double amount, int transaction_count_24h) {
    // Simple velocity-based risk calculation
    double base_risk = (amount / 1000.0) * 2.5;
    double velocity_multiplier = 1.0 + (transaction_count_24h * 0.15);
    double risk = base_risk * velocity_multiplier;
    return std::min(100.0, risk);
}

double batch_process(const std::vector<double>& amounts) {
    double total = 0.0;
    for (double amt : amounts) total += amt;
    return total;
}

PYBIND11_MODULE(fast_math, m) {
    m.doc() = "MAZI High-Performance Risk Calculations";
    m.def("calculate_risk_score", &calculate_risk_score, 
          "Calculate risk based on amount and velocity");
    m.def("batch_process", &batch_process, 
          "Sum amounts quickly");
}