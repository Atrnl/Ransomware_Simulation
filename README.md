# RANSOMWARE SIMULATION 

# Project Ovwerview
This repository contains a ransomware simulation built for educational purposes (encryption + simulated ransom note + corresponding decryption flow). The goal is to learn how ransomware works so you can build detection and mitigation techniques — not to deploy on real systems.

# Components
- encryptor.py — Main simulation: scans target folder, encrypts files (limited to test file types here), generates an AES key, encrypts the AES key with an RSA public key, saves encrypted_key.bin, and drops a ransom note.
- decryptor.py — Attacker-side (or recovery) script: uses RSA private key to decrypt

# Working

encryption-

<img width="510" height="435" alt="image" src="https://github.com/user-attachments/assets/200fb03d-4824-47c7-ace3-f8adfc5b9e7c" />

decryption - 

<img width="556" height="295" alt="image" src="https://github.com/user-attachments/assets/564723cc-d9d3-4b9d-a077-539be6243c8e" />


