"""
Client-side encryption utilities for password security
"""
try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
    from Crypto.Protocol.KDF import PBKDF2
    from Crypto.Hash import SHA256
    print("✅ PyCryptodome imports successful")
except ImportError:
    print("❌ PyCryptodome import failed")
    raise
import base64
import json
import os
from typing import Dict, Any
import logging

logger = logging.getLogger("BookLibraryAPI")

class PasswordEncryption:
    """
    Handles client-side password encryption to prevent passwords
    from appearing in browser network requests in plain text
    """
    
    def __init__(self):
        # Use a fixed salt for consistency (in production, use environment variable)
        self.salt = b'book_library_2025_salt_key_fixed'
        self.key_length = 32  # 256 bits
        self.iterations = 100000  # PBKDF2 iterations
        
    def generate_key(self, master_password: str = "BookLibrary2025!") -> bytes:
        """Generate encryption key from master password"""
        return PBKDF2(
            master_password,
            self.salt,
            self.key_length,
            count=self.iterations,
            hmac_hash_module=SHA256
        )
    
    def encrypt_password(self, password: str, master_key: str = "BookLibrary2025!") -> Dict[str, str]:
        """
        Encrypt password for client transmission
        
        Returns:
            Dict with encrypted_password and initialization_vector
        """
        try:
            # Generate encryption key
            key = self.generate_key(master_key)
            
            # Create cipher
            cipher = AES.new(key, AES.MODE_GCM)
            
            # Encrypt password
            ciphertext, tag = cipher.encrypt_and_digest(password.encode('utf-8'))
            
            # Encode everything to base64 for JSON transmission
            encrypted_data = {
                'encrypted_password': base64.b64encode(ciphertext).decode('utf-8'),
                'nonce': base64.b64encode(cipher.nonce).decode('utf-8'),
                'tag': base64.b64encode(tag).decode('utf-8'),
                'encrypted': True
            }
            
            logger.info(f"Password encrypted successfully. Length: {len(encrypted_data['encrypted_password'])}")
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Password encryption failed: {str(e)}")
            raise
    
    def decrypt_password(self, encrypted_data: Dict[str, str], master_key: str = "BookLibrary2025!") -> str:
        """
        Decrypt password on server side
        
        Args:
            encrypted_data: Dict containing encrypted_password, nonce, and tag
            master_key: Master encryption key
            
        Returns:
            Decrypted password string
        """
        try:
            # Generate same key
            key = self.generate_key(master_key)
            
            # Decode from base64
            ciphertext = base64.b64decode(encrypted_data['encrypted_password'])
            nonce = base64.b64decode(encrypted_data['nonce'])
            tag = base64.b64decode(encrypted_data['tag'])
            
            # Create cipher with same nonce
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            
            # Decrypt and verify
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            
            decrypted_password = plaintext.decode('utf-8')
            logger.info("Password decrypted successfully")
            return decrypted_password
            
        except Exception as e:
            logger.error(f"Password decryption failed: {str(e)}")
            raise ValueError("Failed to decrypt password")

# Global instance
password_encryptor = PasswordEncryption()

def encrypt_login_data(email: str, password: str) -> Dict[str, Any]:
    """
    Convenience function to encrypt login data
    """
    encrypted_pwd = password_encryptor.encrypt_password(password)
    return {
        'email': email,
        'password': encrypted_pwd['encrypted_password'],
        'nonce': encrypted_pwd['nonce'],
        'tag': encrypted_pwd['tag'],
        'encrypted': True
    }

def decrypt_login_data(login_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Convenience function to decrypt login data
    """
    if not login_data.get('encrypted', False):
        # Not encrypted, return as-is (backward compatibility)
        return {
            'email': login_data['email'],
            'password': login_data['password']
        }
    
    # Decrypt password
    encrypted_data = {
        'encrypted_password': login_data['password'],
        'nonce': login_data['nonce'],
        'tag': login_data['tag']
    }
    
    decrypted_password = password_encryptor.decrypt_password(encrypted_data)
    
    return {
        'email': login_data['email'],
        'password': decrypted_password
    }
