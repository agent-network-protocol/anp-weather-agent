"""
JWT configuration module providing functions to get JWT public and private keys.
"""

import os
import logging
from typing import Optional
from config import JWT_PRIVATE_KEY_PATH, JWT_PUBLIC_KEY_PATH

# 确保密钥文件存在
if not os.path.exists(JWT_PRIVATE_KEY_PATH):
    raise FileNotFoundError(f"JWT private key not found at: {JWT_PRIVATE_KEY_PATH}")
if not os.path.exists(JWT_PUBLIC_KEY_PATH):
    raise FileNotFoundError(f"JWT public key not found at: {JWT_PUBLIC_KEY_PATH}")


def get_jwt_private_key(key_path: str = JWT_PRIVATE_KEY_PATH) -> Optional[str]:
    """
    Get the JWT private key from a PEM file.

    Args:
        key_path: Path to the private key PEM file (default: from config)

    Returns:
        Optional[str]: The private key content as a string, or None if the file cannot be read
    """
    if not os.path.exists(key_path):
        logging.error(f"Private key file not found: {key_path}")
        return None

    try:
        with open(key_path, "r") as f:
            private_key = f.read()
        logging.info(f"Successfully read private key from {key_path}")
        return private_key
    except Exception as e:
        logging.error(f"Error reading private key file: {e}")
        return None


def get_jwt_public_key(key_path: str = JWT_PUBLIC_KEY_PATH) -> Optional[str]:
    """
    Get the JWT public key from a PEM file.

    Args:
        key_path: Path to the public key PEM file (default: from config)

    Returns:
        Optional[str]: The public key content as a string, or None if the file cannot be read
    """
    if not os.path.exists(key_path):
        logging.error(f"Public key file not found: {key_path}")
        return None

    try:
        with open(key_path, "r") as f:
            public_key = f.read()
        logging.info(f"Successfully read public key from {key_path}")
        return public_key
    except Exception as e:
        logging.error(f"Error reading public key file: {e}")
        return None


# # Example usage
# if __name__ == "__main__":
#     # Print the absolute paths being used
#     print(f"Private key path: {JWT_PRIVATE_KEY_PATH}")
#     print(f"Public key path: {JWT_PUBLIC_KEY_PATH}")

#     # Get keys
#     private_key = get_jwt_private_key()
#     public_key = get_jwt_public_key()

#     # Display key information
#     if private_key:
#         print("\n=== Private Key ===")
#         print(private_key)
#         print(f"Size: {len(private_key)} bytes")
#     else:
#         print("\nFailed to read private key")

#     if public_key:
#         print("\n=== Public Key ===")
#         print(public_key)
#         print(f"Size: {len(public_key)} bytes")
#     else:
#         print("\nFailed to read public key")
