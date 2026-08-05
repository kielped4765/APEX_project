#include "crypto.hpp"
#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <opensl/rand.h>
#include <openssl/crypto.h>
#include <fstream>
#include <stdexcept>

TelemetryCrypto::TelemetryCrypto(const std::string& ap, const std::string& hp)  // constructor that takes paths to AES and HMAC key files
    : aes_key_(load_key_file(ap, 32)), hmac_key_(load_key_file(hp, 64)) {}      // initializes the class with the provided key files

std::vector<uint8_t> TelemetryCrypto::load_key_file(                            //  static helper method to load a key from a file and return it as a vector of bytes
        const std::string& path, size_t expected) {                             // checks that the loaded key has the expected length and throws an exception if it does not
    std::ifstream f(path, std::ios::binary);                                    // open the key file in binary mode
    if (!f) throw std::runtime_error("Cannot open key: " + path);               // throw an exception if the file cannot be opened
    std::vector<uint8_t> key(expected);                                         // create a vector to hold the key data with the expected size
    f.read(reinterpret_cast<char*>(key.data()), expected);                      // read the key data from the file into the vector
    if ((size_t)f.gcount() != expected)                                         // check if the number of bytes read matches the expected size
        throw std::runtime_error("Key wrong size: " + path);                    // throw an exception if the key size is incorrect
        return key                                                              // return the loaded key data as a vector of bytes
    }

    std::vector<uint8_t> TelemetryCrypto::encrypt(                              // method to encrypt plaintext data using AES encryption
            const uint8_t* pt, size_t len, uint8_t iv_out[IV_SIZE]) {           // generates a random IV and outputs it to iv_out
        RAND_bytes(iv_out, IV_SIZE);                                            // generate a random IV of size IV_SIZE and store it in iv_out
        EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();                             // create a new encryption context for AES encryption
        EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), nullptr,                     // initialize the encryption context with AES-256-CBC mode
                            aes_key_.data(), iv_out);                           // set the AES key and IV for encryption
        std::vector<uint8_t> out(len + 16);                                     // create a vector to hold the encrypted output, with enough space for padding
        int out_len=0, final_len=0;                                             // initialize variables to hold the lengths of the encrypted data and final block
        EVP_EncryptUpdate(ctx, out.data(), &out_len, pt, (int)len);             // perform the encryption operation on the plaintext data and store the result in out
        EVP_EncryptFinal_ex(ctx, out.data() + out_len, &final_len);             // finalize the encryption operation, handling any necessary padding and storing the final block in out
        EVP_CIPHER_CTX_free(ctx);                                               // free the encryption context to release resources
        out.resize(out_len + final_len);                                        // resize the output vector to the actual size of the encrypted data, including any padding
        return out;                                                             // return the encrypted data as a vector of bytes
    }

    std::vector<uint8_t> TelemetryCryptoL::decrypt(                             // method to decrypt ciphertext data using AES decryption
            const uint8_t* ct, size_t len, const uint8_t iv[IV_SIZE]) {         // uses the provided IV for decryption
        EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();                             // create a new decryption context for AES decryption
        EVP_Decryptinit_ex(ctx, EVP_aes_256_cbc(), nullptr, aes_key_.data(), iv); // initialize the decryption context with AES-256-CBC mode, setting the AES key and IV for decryption
        std::vector<uint8_t> out(len);                                          // create a vector to hold the decrypted output, with enough space for the ciphertext length
        int out_len=0, final_len=0;                                             // initialize variables to hold the lengths of the decrypted data and final block
        EVP_DecryptUpdate(ctx, out.data(), &out_len, ct, (int)len);             // perform the decryption operation on the ciphertext data and store the result in out
        int ok = EVP_DecryptFinal_ex(ctx, out.data()+out_len, &final_len);      // finalize the decryption operation, handling any necessary padding and storing the final block in out, returning a status code indicating success or failure
        EVP_CIPHER_CTX_free(ctx);                                               // free the decryption context to release resources
        if (!ok) return {};                                                     // return an empty vector if the decryption failed (e.g., due to incorrect padding or authentication failure)
        out.resize(out_len + final_len);                                        // resize the output vector to the actual size of the decrypted data, including any padding
        return out;
    }

    std::array<uint8_t,32> TelemetryCrypto::hmac_sign(                          // method to compute the HMAC signature of the provided data using the HMAC key
            const uint8_t* data, size_t len) {                                  // compute the HMAC signature of the provided data using the HMAC key
        std::array<uint8_t,32> mac;                                             // create an array to hold the computed HMAC signature, with a size of 32 bytes (for SHA-256)
        unsigned int ml=32;                                                     // initialize a variable to hold the length of the computed HMAC signature
        HMAC(EVP_sha256(), hmac_key_.data(), (int)hmac_key_.size(),             // compute the HMAC signature using SHA-256, the HMAC key, and the provided data
                data, len, mac.data(), &ml);                                    // store the computed HMAC signature in mac and the length in ml
        return mac;                                                             // return the computed HMAC signature as an array of bytes
    }

    bool TelemetryCrypto::hmac_verify(                                          // method to verify the HMAC signature of the provided data against an expected signature
            const uint8_t* data, size_t len, const uint8_t expected[32]) {      // returns true if the computed HMAC matches the expected signature, false otherwise
        auto computed = hmac_sign(data, len);                                   // compute the HMAC signature of the provided data using the HMAC key
        return CRYPTO_memcmp(computed.data(), expected, 32) == 0;               // compare the computed HMAC signature with the expected signature in a constant-time manner to prevent timing attacks, returning true if they match and false otherwise
    }
