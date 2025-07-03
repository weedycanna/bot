from pathlib import Path

from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub


def setup_localization():
    locales_dir = Path(__file__).parent / "locales"

    en_translator = FluentTranslator(
        locale="en",
        translator=FluentBundle.from_files(
            locale="en", filenames=[str(locales_dir / "en.ftl")]
        ),
    )

    ru_translator = FluentTranslator(
        locale="ru",
        translator=FluentBundle.from_files(
            locale="ru", filenames=[str(locales_dir / "ru.ftl")]
        ),
    )

    translator_hub = TranslatorHub(
        locales_map={
            "en": ("en",),
            "ru": ("ru",),
        },
        translators=[en_translator, ru_translator],
        root_locale="en",
    )

    return translator_hub
