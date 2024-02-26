from cryptography.fernet import Fernet

# Функция генерации ключа 
def generate_key():
    key = Fernet.generate_key()
    return key

# Функция шифрования пароля
def encrypt_password(password, key):
    cipher = Fernet(key)
    encrypted_password = cipher.encrypt(password.encode())
    return encrypted_password

# Функция расшифрования пароля
def decrypt_password(encrypted_password, key):
    cipher = Fernet(key)
    decrypted_password = cipher.decrypt(encrypted_password).decode()
    return decrypted_password
