#pragma once
#include "aircraft.hpp"
#include <atomic>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <cstring>
#include <stdexcept>
#include <array>

constexpr size_t RING_SIZE = 128;       // Size of the ring buffer

struct SharedRingBuffer {
    alignas(64) std::atomic<uint64_t> write_idx{0};     // our engine that prevents false sharing and forces onto seperate CPU cache lines
    alignas(64)  std::atomic<uint64_t> read_idx{0};      // broker only and pushes new line
    std::array<AircraftState, RING_SIZE> slots;         // Holds data slots in ring buffer

};

// Writer set at 50 Hz
inline void ring_push(SharedRingBuffer& rb, const AircraftState& s) {   // prints inline directly into the caller to avoid function-call overhead
    uint64_t idx = rb.write_idx.load(std::memory_order_relaxed);        // fetches current write position index within the ring buffer
    rb.slots[idx % RING_SIZE] = s;                                      // calculates the exact array slot using modulo operator
    rb.write_idx.fetch_add(1, std::memory_order_release);               // increases write index by 1 and applies a release memory fence
}

// Reader - returns false if empty
inline bool ring_pop(SharedRingBuffer& rb, AircraftState& out) {        // returns true or false depending on successfully reading data
    uint64_t w = rb.write_idx.load(std::memory_order_acquire);          // loads current write index memory
    uint64_t r = rb.read_idx.load(std::memory_order_relaxed);           // loads current read index memory
    if (w == r) return false;                                           // if write index equals read index, return false
    out = rb.slots[r % RING_SIZE];                                      // copies aircraft data from the correct slot in array
    rb.read_idx.fetch_add(1, std::memory_order_release);                // atomically increases read index by 1 and applies a release memory fence
    return true;                                                        // return true to indicate successful read
}

inline SharedRingBuffer* create_shared_ring(const char* name) {
    int fd = shm_open(name, O_CREAT | O_RDWR, 0666);                    // Opens a shared memory object with read/write permissions
    ftruncate(fd, sizeof(SharedRingBuffer));
    void* ptr = mmap(nullptr, sizeof(SharedRingBuffer),
                     PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);        // Maps the shared memory object into the process's address space
    close(fd);                                                          // Closes the file descriptor for the shared memory object
    return new(ptr) SharedRingBuffer();
}

inline SharedRingBuffer* open_shared_ring(const char* name) {
    int fd = shm_open(name, O_RDWR, 0666);                          // Opens an existing shared memory object with read/write permissions
    void* ptr = mmap(nullptr, sizeof(SharedRingBuffer),
                     PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);    // Maps the shared memory object into the process's address space
    close(fd);                                                      // Closes the file descriptor for the shared memory object
    return reinterpret_cast<SharedRingBuffer*>(ptr);                // Returns a pointer to the mapped shared memory region
}
