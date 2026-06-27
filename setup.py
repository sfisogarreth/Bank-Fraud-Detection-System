from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        "fast_math",
        ["fast_math.cpp"],
        # This automatically finds where pybind11 is installed on your machine
        include_dirs=[pybind11.get_include()],
        language='c++'
    ),
]

setup(
    name="fast_math",
    ext_modules=ext_modules,
)