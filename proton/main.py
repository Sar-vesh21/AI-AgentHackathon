# import os
# from dotenv import load_dotenv
# from protonmail import ProtonMail

# # Load credentials from environment variables
# load_dotenv()
# username = os.getenv("PROTON_USERNAME")
# password = os.getenv("PROTON_PASSWORD")

# try:
#     proton = ProtonMail()
#     proton.login(username, password)

#     # Get a list of all messages
#     messages = proton.get_messages()
#     print(messages)

# except Exception as e:
#     print(f"Error occurred: {str(e)}")

from typing import Optional
import requests
from requests import Session

class ProtonMailAuth:
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    def __init__(self, proxy: Optional[str] = None, logging_level: Optional[int] = 2, logging_func: Optional[callable] = print):
        self.proxy = proxy
        self.logging_level = logging_level
        self.logging_func = logging_func
        
        self.session = Session()
        self.session.proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else dict()
        self.session.headers.update(self.DEFAULT_HEADERS)

    def _parse_info_before_login(self, info, password: str) -> tuple[str, str, str]:
        verified = self.pgp.message(info['Modulus'])
        modulus = b64decode(verified.message)
        server_challenge = b64decode(info['ServerEphemeral'])
        salt = b64decode(info['Salt'])
        spr_session = info['SRPSession']

        self.user = User(password, modulus)
        client_challenge = b64encode(self.user.get_challenge()).decode('utf8')
        client_proof = b64encode(self.user.process_challenge(salt, server_challenge)).decode('utf8')

        return client_challenge, client_proof, spr_session

    def login(self, username: str, password: str, getter_2fa_code: callable = lambda: input("enter 2FA code:")) -> None:
        data = {'Username': username}

        # Get auth info
        info = self.session.post('https://api.protonmail.ch/auth/info', json=data).json()
        
        if 'Error' in info:
            raise Exception(f"Failed to get auth info: {info['Error']}")

        # Generate cryptographic proof
        try:
            client_challenge, client_proof, spr_session = self._parse_info_before_login(info, password)
        except Exception as e:
            raise Exception(f"Failed to generate authentication proof: {str(e)}")

        # Attempt authentication
        auth_response = self.session.post('https://api.protonmail.ch/auth', json={
            'Username': username,
            'ClientEphemeral': client_challenge,
            'ClientProof': client_proof,
            'SRPSession': spr_session,
            'PersistentCookies': 1,
        }).json()

        if 'Error' in auth_response:
            raise Exception(f"Authentication failed: {auth_response['Error']}")

        if 'ServerProof' not in auth_response:
            raise Exception("Server proof missing from authentication response")

        # Handle 2FA if needed
        if auth_response.get('2FA', {}).get('Enabled'):
            twofa_code = getter_2fa_code()
            # Implement 2FA verification here
            # This would need another request to verify the 2FA code

        # At this point, authentication should be successful
        self.logging_func(f"Successfully authenticated as {username}")