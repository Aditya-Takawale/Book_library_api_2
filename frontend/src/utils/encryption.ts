/**
 * Client-side password encryption for secure transmission
 * Uses Web Crypto API for AES-GCM encryption
 */
export class PasswordEncryptor {
  private salt = new TextEncoder().encode('book_library_2025_salt_key_fixed');
  private keyLength = 256; // bits
  private iterations = 100000;
  private masterPassword = 'BookLibrary2025!';

  /**
   * Generate encryption key using PBKDF2
   */
  private async generateKey(masterPassword = this.masterPassword): Promise<CryptoKey> {
    const keyMaterial = await window.crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(masterPassword),
      { name: 'PBKDF2' },
      false,
      ['deriveKey']
    );

    return await window.crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: this.salt,
        iterations: this.iterations,
        hash: 'SHA-256'
      },
      keyMaterial,
      {
        name: 'AES-GCM',
        length: this.keyLength
      },
      false,
      ['encrypt', 'decrypt']
    );
  }

  /**
   * Encrypt password for secure transmission
   */
  async encryptPassword(password: string): Promise<{
    encrypted_password: string;
    nonce: string;
    tag: string;
    encrypted: boolean;
  }> {
    try {
      console.log('🔒 Starting password encryption...');
      
      // Generate encryption key
      const key = await this.generateKey();
      
      // Generate random IV/nonce
      const nonce = window.crypto.getRandomValues(new Uint8Array(12));
      
      // Encrypt password
      const encrypted = await window.crypto.subtle.encrypt(
        {
          name: 'AES-GCM',
          iv: nonce
        },
        key,
        new TextEncoder().encode(password)
      );

      // Extract ciphertext and tag
      const encryptedArray = new Uint8Array(encrypted);
      const ciphertext = encryptedArray.slice(0, -16); // All but last 16 bytes
      const tag = encryptedArray.slice(-16); // Last 16 bytes

      // Convert to base64 for JSON transmission
      const result = {
        encrypted_password: this.arrayBufferToBase64(ciphertext),
        nonce: this.arrayBufferToBase64(nonce),
        tag: this.arrayBufferToBase64(tag),
        encrypted: true
      };

      console.log('✅ Password encrypted successfully');
      return result;

    } catch (error) {
      console.error('❌ Password encryption failed:', error);
      throw new Error('Failed to encrypt password');
    }
  }

  /**
   * Convert ArrayBuffer to base64 string
   */
  private arrayBufferToBase64(buffer: ArrayBuffer | Uint8Array): string {
    const bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
  }

  /**
   * Encrypt login data for API submission
   */
  async encryptLoginData(email: string, password: string): Promise<{
    email: string;
    password: string;
    nonce: string;
    tag: string;
    encrypted: boolean;
  }> {
    try {
      console.log(`🔐 Encrypting login data for: ${email}`);
      
      const encryptedPassword = await this.encryptPassword(password);
      
      const loginData = {
        email: email,
        password: encryptedPassword.encrypted_password,
        nonce: encryptedPassword.nonce,
        tag: encryptedPassword.tag,
        encrypted: true
      };

      console.log('✅ Login data encrypted successfully');
      return loginData;

    } catch (error) {
      console.error('❌ Login data encryption failed:', error);
      throw error;
    }
  }
}

// Global instance for easy access
export const passwordEncryptor = new PasswordEncryptor();
