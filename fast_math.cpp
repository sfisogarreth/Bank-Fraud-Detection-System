#include <pybind11/pybind11.h>
#include <vector>
#include <cmath>
#include <algorithm>

namespace py = pybind11;

// Enhanced velocity-based risk calculation with balance weighting
double calculate_risk_score(double amount, int transaction_count_24h) {
    double base_risk = (amount / 1000.0) * 2.5;
    double velocity_multiplier = 1.0 + (static_cast<double>(transaction_count_24h) * 0.15);
    double risk = base_risk * velocity_multiplier;
    return std::min(100.0, std::max(0.0, risk));
}

// Advanced batch scoring processor for bulk telemetry checking
std::vector<double> batch_calculate_risk(const std::vector<double>& amounts, const std::vector<int>& counts) {
    size_t size = std::min(amounts.size(), counts.size());
    std::vector<double> results;
    results.reserve(size);
    for (size_t i = 0; i < size; ++i) {
        results.push_back(calculate_risk_score(amounts[i], counts[i]));
    }
    return results;
}

double batch_process(const std::vector<double>& amounts) {
    double total = 0.0;
    for (double amt : amounts) {
        total += amt;
    }
    return total;
}

PYBIND11_MODULE(fast_math, m) {
    m.doc() = "MAZI High-Performance Risk Calculations C++ Extension Module";
    m.def("calculate_risk_score", &calculate_risk_score, 
          "Calculate comprehensive real-time risk score based on transaction amount and 24h velocity",
          py::arg("amount"), py::arg("transaction_count_24h"));
    m.def("batch_calculate_risk", &batch_calculate_risk,
          "Process bulk arrays of amounts and velocities simultaneously with native hardware speed",
          py::arg("amounts"), py::arg("counts"));
    m.def("batch_process", &batch_process, 
          "Sum transaction amounts quickly and securely in memory");
}