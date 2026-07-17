from setuptools import setup
from torch.utils.cpp_extension import CppExtension, BuildExtension

ext = CppExtension(
    name="mydev._C",
    sources=[
        "cpp/ops/allocator.cpp",
        "cpp/ops/ops.cpp",
        "cpp/ops/add.cpp",
        "cpp/ops/sub.cpp",
        "cpp/ops/backend.cpp",
        "cpp/ops/init.cpp",
    ],
    extra_compile_args=["-std=c++17"],
)

setup(
    ext_modules=[ext],
    cmdclass={"build_ext": BuildExtension},
)
