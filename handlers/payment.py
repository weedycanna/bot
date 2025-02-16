from http import HTTPStatus
from typing import Union

import aiohttp


async def get_crypto_rate(crypto: str, fiat: str = 'USD') -> Union[float, None]:

    url: str = f'https://min-api.cryptocompare.com/data/price?fsym={crypto}&tsyms={fiat}'

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == HTTPStatus.OK:
                    data = await response.json()
                    rate = data.get(fiat)
                    if rate is None:
                        return None
                    return float(rate)
    except ConnectionError:
        return None


async def convert_to_crypto(amount: float, fiat: str, crypto: str) -> Union[float, None]:
    rate = await get_crypto_rate(crypto, fiat)
    if rate is None:
        return None

    return amount / rate


