from decimal import Decimal

from handlers.payment import CryptoApiManager


async def convert_currency(amount_usd, user_language: str) -> tuple[Decimal, str]:
    amount_usd = Decimal(amount_usd)
    if user_language == "ru":
        usd_to_rub = await CryptoApiManager.get_usd_to_rub_rate()
        usd_to_rub = Decimal(str(usd_to_rub))
        return amount_usd * usd_to_rub, "₽"
    else:
        return amount_usd, "$"


def format_price(amount: Decimal, currency: str) -> str:
    if currency == "₽":
        return f"{amount:.0f} {currency}"
    else:
        return f"{amount:.2f} {currency}"
