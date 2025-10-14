from pathlib import Path
import platform


def is_cpython() -> bool:
    """Проверить, что используется `CPython`."""
    return platform.python_implementation() == "CPython"


def is_linux() -> bool:
    """Проверить, что используется `Linux`."""
    return platform.system() == "Linux"


def is_windows() -> bool:
    """Проверить, что используется `Windows`."""
    return platform.system() == "Windows"



def is_supported_platform() -> bool:
    """Проверить, что платформа поддерживается."""


def is_supported_python_version() -> bool:
    """Проверить, что версия `Python` поддерживается."""


def get_cpython_root() -> Path:
    """Получить путь до корня `CPython`."""


def get_interface_library() -> Path | None:
    """Получить путь до библиотеки-интерфейса, если она требуется."""


def get_shared_library() -> Path:
    """Получить путь до разделяемой библиотеки."""


def get_header_files() -> list[Path]:
    """Получить список загловочных файлов."""


def get_build_file_contents() -> str:
    """Получить содержимое файла `BUILD.bazel`"""


def main() -> None:
    """Запустить скрипт."""


if __name__ == "__main__":
    main()
