import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
import zipfile
import threading
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64
import random

# ==========================================
# ADVANCED ENCRYPTION & SECURE WIPE LOGIC
# ==========================================

def generate_key(password: str, salt: bytes) -> bytes:
    """Converts a text password + random salt into a secure key."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000, # High iterations slow down brute-force attacks
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def secure_wipe(filepath: str):
    """Overwrites the file with random garbage before deleting to prevent recovery."""
    try:
        filesize = os.path.getsize(filepath)
        with open(filepath, 'wb') as f:
            f.write(os.urandom(filesize)) # Overwrite with random bytes
        os.remove(filepath) # Now safely delete
    except:
        os.remove(filepath) # Fallback to normal delete if permission denied

def encrypt_file(filepath: str, password: str):
    """Encrypts a file with a random salt and securely wipes the original."""
    salt = os.urandom(16) # GENERATE RANDOM SALT PER FILE
    key = generate_key(password, salt)
    fernet = Fernet(key)
    
    with open(filepath, 'rb') as file:
        original_data = file.read()
        
    encrypted_data = fernet.encrypt(original_data)
    
    locked_path = filepath + '.locked'
    with open(locked_path, 'wb') as file:
        file.write(salt + encrypted_data) # SAVE SALT INSIDE THE FILE
        
    secure_wipe(filepath) # DESTROY ORIGINAL UNENCRYPTED FILE

def decrypt_file(filepath: str, password: str):
    """Extracts the random salt, decrypts, and safely deletes the locked file."""
    with open(filepath, 'rb') as file:
        data = file.read()
        
    salt = data[:16] # EXTRACT SALT FROM FILE
    encrypted_data = data[16:]
    
    key = generate_key(password, salt)
    fernet = Fernet(key)
    
    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except Exception:
        raise ValueError("Wrong Password or Corrupted File!")
        
    unlocked_path = filepath.replace('.locked', '')
    with open(unlocked_path, 'wb') as file:
        file.write(decrypted_data)
        
    os.remove(filepath) # Delete locked file (no need to wipe, it's encrypted)

# ==========================================
# PREMIUM UI SETUP
# ==========================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class LockerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🔐 Zero-Trust File Locker")
        self.geometry("800x550")
        self.configure(fg_color="#0f172a")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=40, pady=(40, 0))
        
        ctk.CTkLabel(header, text="🔐 Zero-Trust Locker", font=ctk.CTkFont(size=32, weight="bold"), text_color="#60a5fa").pack(anchor="w")
        ctk.CTkLabel(header, text="AES-128 Encryption • Random Salts • Secure Wiping", font=ctk.CTkFont(size=13), text_color="#64748b").pack(anchor="w")

        self.tabview = ctk.CTkTabview(self, fg_color="#1e293b", segmented_button_fg_color="#0f172a", segmented_button_selected_color="#3b82f6", segmented_button_unselected_color="#334155")
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=40, pady=30)
        
        self.tab_lock = self.tabview.add("  🔒 Lock  ")
        self.tab_unlock = self.tabview.add("  🔓 Unlock  ")

        self.setup_lock_tab()
        self.setup_unlock_tab()

    # ==========================================
    # TAB 1: LOCK FILES/FOLDERS
    # ==========================================
    def setup_lock_tab(self):
        self.tab_lock.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.tab_lock, text="Select a file or folder to encrypt.", font=ctk.CTkFont(size=14), text_color="#94a3b8").pack(pady=(20, 10))

        self.lock_path = ctk.StringVar()
        path_frame = ctk.CTkFrame(self.tab_lock, fg_color="transparent")
        path_frame.pack(fill="x", padx=30, pady=5)
        
        ctk.CTkEntry(path_frame, textvariable=self.lock_path, height=45, placeholder_text="Path...", fg_color="#0f172a", border_color="#334155").pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(path_frame, text="File", width=80, fg_color="#3b82f6", command=lambda: self.lock_path.set(filedialog.askopenfilename())).pack(side="left", padx=5)
        ctk.CTkButton(path_frame, text="Folder", width=80, fg_color="#3b82f6", command=lambda: self.lock_path.set(filedialog.askdirectory())).pack(side="left")

        ctk.CTkLabel(self.tab_lock, text="Set a strong password:", font=ctk.CTkFont(size=14), text_color="#94a3b8").pack(pady=(20, 5))
        self.lock_pass = ctk.StringVar()
        ctk.CTkEntry(self.tab_lock, textvariable=self.lock_pass, placeholder_text="Password", show="*", height=45, fg_color="#0f172a", border_color="#334155").pack(fill="x", padx=30, pady=5)
        
        self.lock_pass_confirm = ctk.StringVar()
        ctk.CTkEntry(self.tab_lock, textvariable=self.lock_pass_confirm, placeholder_text="Confirm Password", show="*", height=45, fg_color="#0f172a", border_color="#334155").pack(fill="x", padx=30, pady=5)

        self.lock_btn = ctk.CTkButton(self.tab_lock, text="🔒 Lock & Secure Wipe Original", fg_color="#ef4444", hover_color="#dc2626", font=ctk.CTkFont(size=16, weight="bold"), height=50, command=self.start_lock_thread)
        self.lock_btn.pack(fill="x", padx=30, pady=(30, 10))
        
        self.lock_status = ctk.StringVar(value="")
        ctk.CTkLabel(self.tab_lock, textvariable=self.lock_status, text_color="#60a5fa", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=10)

        ctk.CTkLabel(self.tab_lock, text="⚠️ WARNING: If you forget the password, your files CANNOT be recovered!\nOriginals are securely overwritten to prevent recovery.", font=ctk.CTkFont(size=11), text_color="#f87171").pack(pady=(10, 0))

    def start_lock_thread(self):
        path = self.lock_path.get()
        pw = self.lock_pass.get()
        pw_c = self.lock_pass_confirm.get()

        if not path or not os.path.exists(path): return messagebox.showwarning("Error", "Select a valid file or folder.")
        if not pw or len(pw) < 6: return messagebox.showwarning("Error", "Password must be at least 6 characters.")
        if pw != pw_c: return messagebox.showwarning("Error", "Passwords do not match!")

        self.lock_btn.configure(state="disabled", text="Processing...")
        self.lock_status.set("Compressing & Wiping... This may take a moment for large folders.")
        threading.Thread(target=self.do_lock, args=(path, pw), daemon=True).start()

    def do_lock(self, path, pw):
        try:
            if os.path.isdir(path):
                self.after(0, lambda: self.lock_status.set("Compressing folder..."))
                zip_path = path + ".zip"
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for root, _, files in os.walk(path):
                        for file in files:
                            zf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))
                
                # Securely wipe the original folder contents before deleting
                self.after(0, lambda: self.lock_status.set("Securely wiping original files..."))
                for root, _, files in os.walk(path):
                    for file in files:
                        secure_wipe(os.path.join(root, file))
                        
                shutil.rmtree(path) 
                path = zip_path 

            self.after(0, lambda: self.lock_status.set("Encrypting data..."))
            encrypt_file(path, pw)
            
            self.after(0, lambda: self.lock_status.set("✅ Successfully Locked & Wiped!"))
            self.after(0, lambda: messagebox.showinfo("Success", "Locked securely!"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to lock:\n{str(e)}"))
        finally:
            self.after(0, lambda: self.lock_btn.configure(state="normal", text="🔒 Lock & Secure Wipe Original"))
            self.after(0, lambda: self.lock_status.set(""))


    # ==========================================
    # TAB 2: UNLOCK FILES/FOLDERS
    # ==========================================
    def setup_unlock_tab(self):
        self.tab_unlock.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.tab_unlock, text="Select a .locked file to decrypt.", font=ctk.CTkFont(size=14), text_color="#94a3b8").pack(pady=(20, 10))

        self.unlock_path = ctk.StringVar()
        path_frame = ctk.CTkFrame(self.tab_unlock, fg_color="transparent")
        path_frame.pack(fill="x", padx=30, pady=5)
        
        ctk.CTkEntry(path_frame, textvariable=self.unlock_path, height=45, placeholder_text="Path...", fg_color="#0f172a", border_color="#334155").pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(path_frame, text="File", width=80, fg_color="#3b82f6", command=lambda: self.unlock_path.set(filedialog.askopenfilename(filetypes=[("Locked Files", "*.locked")]))).pack(side="left")

        ctk.CTkLabel(self.tab_unlock, text="Enter your password:", font=ctk.CTkFont(size=14), text_color="#94a3b8").pack(pady=(20, 5))
        self.unlock_pass = ctk.StringVar()
        ctk.CTkEntry(self.tab_unlock, textvariable=self.unlock_pass, placeholder_text="Password", show="*", height=45, fg_color="#0f172a", border_color="#334155").pack(fill="x", padx=30, pady=5)

        self.unlock_btn = ctk.CTkButton(self.tab_unlock, text="🔓 Unlock & Decrypt", fg_color="#22c55e", hover_color="#16a34a", font=ctk.CTkFont(size=16, weight="bold"), height=50, command=self.start_unlock_thread)
        self.unlock_btn.pack(fill="x", padx=30, pady=(30, 10))
        
        self.unlock_status = ctk.StringVar(value="")
        ctk.CTkLabel(self.tab_unlock, textvariable=self.unlock_status, text_color="#60a5fa", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=10)

    def start_unlock_thread(self):
        path = self.unlock_path.get()
        pw = self.unlock_pass.get()

        if not path or not path.endswith('.locked'): return messagebox.showwarning("Error", "Select a valid .locked file.")
        if not pw: return messagebox.showwarning("Error", "Enter the password.")

        self.unlock_btn.configure(state="disabled", text="Decrypting...")
        self.unlock_status.set("Processing...")
        threading.Thread(target=self.do_unlock, args=(path, pw), daemon=True).start()

    def do_unlock(self, path, pw):
        try:
            self.after(0, lambda: self.unlock_status.set("Decrypting data..."))
            decrypt_file(path, pw)
            
            unlocked_path = path.replace('.locked', '')
            if unlocked_path.endswith('.zip'):
                self.after(0, lambda: self.unlock_status.set("Extracting folder..."))
                with zipfile.ZipFile(unlocked_path, 'r') as zf:
                    zf.extractall(os.path.dirname(unlocked_path))
                os.remove(unlocked_path) 

            self.after(0, lambda: self.unlock_status.set("✅ Successfully Unlocked!"))
            self.after(0, lambda: messagebox.showinfo("Success", "Unlocked successfully!"))
        except ValueError:
            self.after(0, lambda: messagebox.showerror("Error", "❌ WRONG PASSWORD!"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to unlock:\n{str(e)}"))
        finally:
            self.after(0, lambda: self.unlock_btn.configure(state="normal", text="🔓 Unlock & Decrypt"))
            self.after(0, lambda: self.unlock_status.set(""))

# ==========================================
# RUN THE APP
# ==========================================
if __name__ == "__main__":
    app = LockerApp()
    app.mainloop()