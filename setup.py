from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        "fast_math",
        ["fast_math.cpp"],
        include_dirs=[pybind11.get_include()],
        language='c++'
    ),
]

setup(
    name="fast_math",
    version="1.0.0",
    author="MAZI AI Engineering Team",
    description="High-performance C++ risk calculation engine for MAZI AI Fraud Detection",
    ext_modules=ext_modules,
)