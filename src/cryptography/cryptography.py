import base64
import datetime
import hashlib
import secrets

RANDOM_STRING_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


class Crypto:
    @staticmethod
    def _hash_passwd(salt: str, passwd: str, iterations: int = 10 ** 5) -> str:
        tmp_hash = hashlib.pbkdf2_hmac(
            "sha3_512", passwd.encode("ascii"), salt.encode("ascii"), iterations
        )
        tmp_hash = base64.b64encode(tmp_hash).decode("ascii").strip()
        return tmp_hash

    @staticmethod
    def get_salt() -> str:
        return "".join(secrets.choice(RANDOM_STRING_CHARS) for _ in range(1024))

    @staticmethod
    def full_passwd(passwd: str) -> str:
        iterations = 10 ** 5
        salt = Crypto.get_salt()
        return (
            f"pbkdf2_sha3_512${str(iterations)}${salt}"
            f"${Crypto._hash_passwd(salt, passwd, iterations)}"
        )

    @staticmethod
    def gen_token_for_auth(user_id: int) -> str:  # TODO: I hope its secure?
        tmp_hash = hashlib.sha3_512()
        tmp_hash.update(str.encode(f"{str(user_id)}{str(datetime.datetime.now())}"))
        return tmp_hash.hexdigest()

    @staticmethod
    def is_correct_password(hashed_password: str, passwd: str) -> bool:
        """
        :param hashed_password: str
        :param passwd: str
        :return: bool
        """
        passwd_list = hashed_password.split("$")
        iterations = int(passwd_list[1])
        salt = passwd_list[2]
        hash_passwd_from_db = passwd_list[3]
        hash_pass = Crypto._hash_passwd(salt, passwd, iterations)
        # INFO: Для того, чтоб не было атак по времени (идея взята из джанги)
        return secrets.compare_digest(
            hash_pass.encode("ascii"), hash_passwd_from_db.encode("ascii")
        )

    @staticmethod
    def gen_token_for_reset_pass(user_login: str) -> str:  # TODO: I hope its secure?
        tmp_hash = hashlib.sha3_512()
        tmp_hash.update(str.encode(f"{str(user_login)}{str(datetime.datetime.now())}"))
        return tmp_hash.hexdigest()
