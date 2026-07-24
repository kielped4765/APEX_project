add_executable(apex_engine
    src/main.cpp
    src/dynamics.cpp
)

# Allows for speed optimization and is private to the apex_engine target
target_include_directories(apex_engine PRIVATE include)
target_compile_options(apex_engine PRIVATE -O2 -Wall -Wextra)