import os
from http import HTTPStatus
from typing import Union

import aiohttp


class CryptoApiManager:
    RATE_API_URL: str = os.getenv("RATE_API_URL")
    REQUEST_TIMEOUT: int = 10

    @classmethod
    async def _make_request(cls, url: str) -> Union[dict, None]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=cls.REQUEST_TIMEOUT) as response:
                    if response.status == HTTPStatus.OK:
                        return await response.json()
                    else:
                        return None
        except (ConnectionError, aiohttp.ClientError):
            return None

    @classmethod
    async def get_crypto_rate(
        cls, crypto: str, fiat: str = "USD"
    ) -> Union[float, None]:
        url: str = f"{cls.RATE_API_URL}?fsym={crypto}&tsyms={fiat}"
        data = await cls._make_request(url)

        if data and (rate := data.get(fiat)) is not None:
            return float(rate)
        return None

    @classmethod
    async def convert_to_crypto(
        cls, amount: float, fiat: str, crypto: str
    ) -> Union[float, None]:
        rate = await cls.get_crypto_rate(crypto, fiat)
        if rate is None:
            return None

        return amount / rate

    @classmethod
    async def get_usd_to_rub_rate(cls) -> Union[float, None]:
        url = f"{cls.RATE_API_URL}?fsym=USD&tsyms=RUB"
        data = await cls._make_request(url)
        if data and (rate := data.get("RUB")) is not None:
            return float(rate)
        return None
