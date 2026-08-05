#pragma once
#include "frame.hpp"
#include <vector>
#include <array>
#include <string>

class TelemetryCrypto {         // creating the TelemetryCrypto class to handle encryption, decryption, and HMAC signing/verification
public:
    TelemetryCrypto(const std::string& aes_key_path,    // constructor that takes paths to AES and HMAC key files
                    const std::string& hmac_key_path);  // initializes the class with the provided key files

    std::vector<uint8_t> encrypt(const uint8_t* plaintext, size_t len,  // method to encrypt plaintext data using AES encryption
                                uint8_t iv_out[IV_SIZE]);               // generates a random IV and outputs it to iv_out

    std::vector<uint8_t> decrypt(const uint8_t* ciphertext, size_t len, // method to decrypt ciphertext data using AES decryption
                                const uint8_t iv[IV_SIZE]);             // uses the provided IV for decryption

    std::array<uint8_t, HMAC_SIZE> hmac_sign(const uint8_t* data, size_t len); // method to compute the HMAC signature of the provided data using the HMAC key

    bool hmac_verify(const uint8_t* data, size_t len,                          // method to verify the HMAC signature of the provided data against an expected signature 
                     const uint8_t expected[HMAC_SIZE]);                       // returns true if the computed HMAC matches the expected signature, false otherwise
private:
    std::vector<uint8_t> aes_key_;                                      // member variable to store the AES encryption key
    std::vector<uint8_t> hmac_key_;                                 // member variable to store the HMAC signing key                  
    static std::vector<uint8_t> load_key_file(                      // static helper method to load a key from a file and return it as a vector of bytes
        const std::string& path, size_t expected_len);              // checks that the loaded key has the expected length and throws an exception if it does not
};