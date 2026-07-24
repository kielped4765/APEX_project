cmake_minimum_required(VERSION 3.20)
project(Network_Threat_Intelligence_and_Detection_Platform VERSION 1.0)

# Instructions for what versions and requirements are needed:

# C++ Version
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Memory Saftey: AddressSanitizer (Linux)
if(CMAKE_BUILD_TYPE STREQUAL "Debug" AND NOT WIN32)
    add_compile_options(-fsanitize=address -fno-omit-frame-pointer)
    add_link_options(-fsanitize=address)

endif()



# Set a clean central output directory for binaries
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Adding subdirectories for our engine and broker modules
add_subdirectory(engine)
add_subdirectory(broker)




