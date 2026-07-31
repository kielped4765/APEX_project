#pragma once
#include <cstdint>          // includes standard fixed-width interger types (like uint32/64/8 etc.)

constexpr uint32_t FRAME_MAGIC  = 0xAE1A1337;   // Defining a magic number used as a unique identifer for verification
constexpr size_t   HMAC_SIZE    = 32;           // Defines the HMac size = 32
constexpr size_t   IV_SIZE      = 16;           // Defines the IV size = 16
constexpr size_t   PAYLOAD_SIZE = 128;          // Defines Payload size = 128

enum class FrameType : uint8_t {                // Strong enumeration mapping message to a single byte
    TELEMETRY = 0X01,
    HEARTBEAT = 0X02,
};

enum class AttackType : uint8_t {               // Enumerates the grount-truth threat labels for ML training
    NONE    = 0x00,
    SPOOF   = 0x01,
    REPLAY  = 0X02,
    CORRUPT = 0X03,
    DRIFT   = 0X04,
};

#pragma pack(push, 1)                           // Tells the compiler to disable struct padding and align fields strictly on 1-byte boundaries
struct TelemetryFrame {                         // Declaration of main binary data structure 
    // storing each data type under these variable names
    uint32_t    magic;
    FrameType   frame_type;
    AttackType  attack_label;
    uint64_t    sequence_num;
    int64_t     timestamp_us;
    uint8_t     iv[IV_SIZE];
    uint8_t     payload[PAYLOAD_SIZE];
    uint8_t     hmac[HMAC_SIZE];
};

// Total: 4+1+1+8+8+16+128+32 = 198 bytes per frame
#pragma pack(pop)                               // Restores the compiler's default alignment settings for subsequent code

