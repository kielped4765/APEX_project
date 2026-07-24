# find the required package on the system
find_package(OpenSSL REQUIRED)

# defining the broker executable target
add_executable(apex_broker
    src/main.cpp
    src/crypto.cpp
    src/attacker.cpp
)

# telling the compiler where to find local header files
target_include_directories(apex_broker PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)

# linking OpenSSL libraries to this target
target_link_libraries(apex_broker PRIVATE OpenSSL::SSL OpenSSL::Crypto)

target_compile_options(apex_broker PRIVATE -O2 -Wall -Wextra)