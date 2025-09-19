/**
 * Client-side password encryption for secure transmission
 * Uses Web Crypto API for AES-GCM encryption
 */

class PasswordEncryptor {
    constructor() {
        // Must match the server-side salt and configuration
        this.salt = new TextEncoder().encode('book_library_2025_salt_key_fixed');
        this.keyLength = 256; // bits
        this.iterations = 100000;
        this.masterPassword = 'BookLibrary2025!';
    }

    /**
     * Generate encryption key using PBKDF2
     */
    async generateKey(masterPassword = this.masterPassword) {
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
    async encryptPassword(password) {
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
            console.log('📊 Encrypted data lengths:', {
                password: result.encrypted_password.length,
                nonce: result.nonce.length,
                tag: result.tag.length
            });

            return result;

        } catch (error) {
            console.error('❌ Password encryption failed:', error);
            throw new Error('Failed to encrypt password');
        }
    }

    /**
     * Convert ArrayBuffer to base64 string
     */
    arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return window.btoa(binary);
    }

    /**
     * Encrypt login data for API submission
     */
    async encryptLoginData(email, password) {
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
window.passwordEncryptor = new PasswordEncryptor();

/**
 * Convenience function for encrypting login forms
 */
async function encryptLogin(email, password) {
    return await window.passwordEncryptor.encryptLoginData(email, password);
}

/**
 * Enhanced fetch function that automatically encrypts login requests
 */
async function secureLogin(email, password, endpoint = '/auth/login') {
    try {
        console.log('🔒 Initiating secure login...');
        
        // Encrypt login data
        const encryptedData = await encryptLogin(email, password);
        
        // Send encrypted request
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(encryptedData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('✅ Secure login successful');
        return result;

    } catch (error) {
        console.error('❌ Secure login failed:', error);
        throw error;
    }
}

/**
 * Demo function to test encryption
 */
async function testEncryption() {
    try {
        const testPassword = 'TestPassword123!';
        console.log('🧪 Testing password encryption...');
        console.log('Original password:', testPassword);
        
        const encrypted = await window.passwordEncryptor.encryptPassword(testPassword);
        console.log('Encrypted result:', encrypted);
        
        console.log('✅ Encryption test completed');
        return encrypted;
        
    } catch (error) {
        console.error('❌ Encryption test failed:', error);
        throw error;
    }
}

// Auto-test on load (remove in production)
if (typeof window !== 'undefined') {
    console.log('🔐 Password encryption system loaded');
    console.log('Available functions: encryptLogin(), secureLogin(), testEncryption()');
}
