import dataclasses

from argparse import ArgumentParser, Namespace
from pathlib import Path


@dataclasses.dataclass
class RecursionSettings:
    """Настройки рекурсии."""


def get_parser() -> ArgumentParser:
    """Получить парсер аргументов командной строки."""


def has_valid_args(args: Namespace) -> tuple[bool, str | None]:
    """Проверить, что аргументы валидны."""


def get_extension(path: Path) -> str:
    """Получить расширение файла (возможно, пустое)."""


def tree(path: Path, settings: RecursionSettings) -> None:
    """Вывести файловое древо."""


def main(argv: list[str] | None = None) -> None:
    """Запустить консольную утилиту."""


if __name__ == "__main__":
    main()