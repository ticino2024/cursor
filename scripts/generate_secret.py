"""Generate a secure secret key for JWT."""

import secrets


def generate_secret_key(length: int = 32) -> str:
    """
    Generate a secure random secret key.
    
    Args:
        length: Length of the secret key in bytes
        
    Returns:
        Hexadecimal secret key
    """
    return secrets.token_hex(length)


if __name__ == "__main__":
    secret_key = generate_secret_key()
    print("Generated Secret Key:")
    print(secret_key)
    print("\nAdd this to your .env file:")
    print(f"SECRET_KEY={secret_key}")
