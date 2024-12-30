'''
  * author 冯自立
  * created at : 2024-12-30 22:55:44
  * description: 
'''
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64


class EncryptDecrypt:
    def __init__(self, key: bytes = None):
        """
        Initialize the EncryptDecrypt class with a 16-byte key.
        If no key is provided, a random one will be generated.
        """
        self.key = key or get_random_bytes(16)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt the plaintext using AES encryption in CBC mode.

        Args:
            plaintext (str): The text to encrypt.

        Returns:
            str: The base64-encoded ciphertext.
        """
        if not plaintext:
            return ''
        cipher = AES.new(self.key, AES.MODE_CBC)
        iv = cipher.iv
        padded_data = pad(plaintext.encode(), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        return base64.b64encode(iv + encrypted).decode()

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt the ciphertext using AES decryption in CBC mode.

        Args:
            ciphertext (str): The base64-encoded ciphertext to decrypt.

        Returns:
            str: The decrypted plaintext.
        """
        if not ciphertext:
            return ""
        raw_data = base64.b64decode(ciphertext)
        iv = raw_data[:AES.block_size]
        encrypted = raw_data[AES.block_size:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
        return decrypted.decode()

    @staticmethod
    def littleParrotEncryptManager():
        return EncryptDecrypt("littleparrot1234".encode('utf-8'))


# Example usage
if __name__ == "__main__":
    # Initialize the class (key will be randomly generated if not provided)
    encrypt_decrypt = EncryptDecrypt.littleParrotEncryptManager()

    # Encrypt a message
    plaintext = "This is a secret message."
    ciphertext = encrypt_decrypt.encrypt(plaintext)
    print("Ciphertext:", ciphertext)

    # Decrypt the message
    decrypted_message = encrypt_decrypt.decrypt(ciphertext)
    print("Decrypted message:", decrypted_message)

    # Ensure the decrypted message matches the original
    assert plaintext == decrypted_message
