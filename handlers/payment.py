from http import HTTPStatus
from typing import Union

import aiohttp


class CryptoApiManager:

    RATE_API_URL: str = "https://min-api.cryptocompare.com/data/price"

    @classmethod
    async def get_crypto_rate(cls, crypto: str, fiat: str = "USD") -> Union[float, None]:

        url: str = f"{cls.RATE_API_URL}?fsym={crypto}&tsyms={fiat}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == HTTPStatus.OK:
                        data = await response.json()
                        rate = data.get(fiat)
                        if rate is None:
                            return None
                        return float(rate)
        except (ConnectionError, aiohttp.ClientError):
            return None


    @classmethod
    async def convert_to_crypto(cls, amount: float, fiat: str, crypto: str) -> Union[float, None]:

        rate = await cls.get_crypto_rate(crypto, fiat)
        if rate is None:
            return None

        return amount / rate




