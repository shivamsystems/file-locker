# **🔐 Zero-Trust File & Folder Locker**
<img width="1293" height="953" alt="image" src="https://github.com/user-attachments/assets/8c72080e-8661-4f0e-be80-a1ab3f883a57" />

<img width="1193" height="890" alt="image" src="https://github.com/user-attachments/assets/24c646ca-93c4-483d-8527-5d1a3aaf5896" />


A premium, locally-hosted, military-grade encryption tool built with Python. Don't just hide your files—destroy the originals.

## **🌟 Why Zero-Trust?**

Most "Folder Lockers" just hide your files or change Windows permissions. A hacker with admin access can bypass those in seconds. **Zero-Trust Locker** uses real AES-256 encryption. If they don't have the password, the data is mathematically unreadable.

## **🛡️ Security Architecture**

- **AES-256 Encryption:** Utilizes the `cryptography` library's Fernet implementation.
- **Dynamic Random Salts:** Every file gets a unique 16-byte salt, preventing pre-computed Rainbow Table attacks.
- **PBKDF2HMAC Key Derivation:** 600,000 iterations. This slows down brute-force attacks to a crawl.
- **Secure Data Wiping (Anti-Forensics):** When you lock a file, the unencrypted original isn't just deleted—it is overwritten with cryptographically secure random bytes (`os.urandom`) before deletion, rendering data recovery software (like Recuva) useless.

## **✨ Features**

- 📂 Lock individual **Files** or entire **Folders**.
- 🗜️ Automatic background ZIP compression for folders before encryption.
- 🎨 Premium Dark-Mode UI built with CustomTkinter.
- 🧵 Multi-threaded operations (the UI never freezes during encryption).
- 🚫 Zero Cloud Dependency. 100% Local processing.

## **🚀 Installation & Usage**

### **Option 1: Run from Source**

1. Clone the repo:
    
    ```bash
    git clone https://github.com/shivamsystems/file-locker.git cd file-locker
    ```
    
2. Install dependencies:
    
    **bash**
    
    pip install customtkinter cryptography
    
3. Run the app:
    
    **bash**
    
    python File_Locker.py
    

### **Option 2: Download the Executable (Windows)**

1. Go to the **Releases** page.
2. Download **`File_Locker.exe`**.
3. Double-click to run. *(Note: Windows Defender may show a "Unrecognized App" prompt due to PyInstaller. Click "More Info" -> "Run Anyway").*

## **⚠️ Disclaimer**

This software uses strong encryption. **If you forget your password, your files CANNOT be recovered.** There is no backdoor. Please test it on dummy files first to ensure you understand how it works. Use responsibly and in compliance with local laws.

## **📜 License**

This project is licensed under the MIT License.

**text**

- --

### Part 2: GitHub Setup

Before pushing to GitHub, you need to make sure you don't upload unnecessary files (like the `build` folder or your virtual environment).

- *1. Create a `.gitignore` file**

In your project folder, create a file named `.gitignore` and paste this:

```text

# Byte-compiled / optimized / DLL files

__pycache__/

- .py[cod]

# PyInstaller build folders

build/

dist/

- .spec

# Virtual Environment

venv/

env/

# OS generated files

Thumbs.db

.DS_Store

**2. Push to GitHub via Terminal**
Open your terminal in the project folder and run:

**powershell**

git init

git add .

git commit -m "Initial commit: Zero-Trust File Locker with secure wiping"

git branch -M main

git remote add origin [https://github.com/YOUR_USERNAME/Zero-Trust-Locker.git]https://github.com/shivamsystems/file-locker.git

git push -u origin main
