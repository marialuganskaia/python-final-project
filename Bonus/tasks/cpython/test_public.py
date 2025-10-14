import ast
import os

from pathlib import Path
from tempfile import gettempdir
from uuid import uuid4

import pytest

from cpython import main


@pytest.fixture(scope="function")
def sandbox() -> Path:
    """Фикстура песочницы."""
    base_dir = Path(gettempdir())

    sandbox_dir = base_dir / str(uuid4())
    sandbox_dir.mkdir(parents=True)

    os.chdir(sandbox_dir)

    return sandbox_dir


@pytest.fixture(scope="function")
def cpython_directory(sandbox: Path) -> Path:
    """Получить путь до директории-песочницы `third_party/cpython`."""
    return sandbox / "third_party" / "cpython"


def get_callable_name(node: ast.Call) -> str:
    """Получить имя вызываемой функции."""
    assert isinstance(node.func, ast.Name)
    return node.func.id


def get_keyword(keywords: list[ast.keyword], name: str) -> ast.keyword:
    """Найти нужный аргумент по ключу."""
    try:
        return next(keyword for keyword in keywords if keyword.arg == name)

    except StopIteration:
        detail = f"Среди аргументов вида ключ-значение не найден аргумент '{name}'"
        raise AssertionError(detail)


def test__build_file(cpython_directory: Path) -> None:
    """Кейс: проверяем валидность файла сборки."""
    main()

    build_file = cpython_directory / "BUILD.bazel"

    try:
        contents = build_file.read_text()
        tree = ast.parse(contents)

    except SyntaxError as exception:
        detail = "Файл `BUILD.bazel` имеет неправильный синтаксис"
        raise AssertionError(detail) from exception

    except FileNotFoundError as exception:
        detail = "Файл `BUILD.bazel` не найден"
        raise AssertionError(detail) from exception

    assert len(tree.body) == 1, "Файл `BUILD.bazel` должен состоять из одной инструкции"

    expression = tree.body[0]
    assert isinstance(expression, ast.Expr)

    cc_import = expression.value
    assert isinstance(
        cc_import, ast.Call
    ), "Файл `BUILD.bazel` не содержит вызов `cc_import`"

    rule_name = get_callable_name(cc_import)
    assert rule_name == "cc_import", "Имя правила не равно `cc_import`"

    assert (
        cc_import.args == []
    ), "Правило `cc_import` не должно содержать позиционных аргументов"
    assert (
        cc_import.keywords != []
    ), "Правило `cc_import` содержит пустые ключ-значение аргументы"

    name_node = get_keyword(cc_import.keywords, "name").value
    assert isinstance(name_node, ast.Constant), "Атрибут 'name' должен быть строкой"

    name = name_node.value
    assert name == "cpython", "Атрибут 'name' не равен \"cpython\""

    visibility_node = get_keyword(cc_import.keywords, "visibility").value
    assert isinstance(
        visibility_node, ast.List
    ), "Атрибут 'visibility' должен быть списком строк"

    visibility = [node.value for node in visibility_node.elts]  # type: ignore
    assert visibility == ["//visibility:public"]

    shared_lib_node = get_keyword(cc_import.keywords, "shared_library").value
    assert isinstance(
        shared_lib_node, ast.Constant
    ), "Атрибут 'shared_library' должен быть строкой"

    shared_library = Path(shared_lib_node.value)
    assert cpython_directory.joinpath(shared_library).exists()

    includes_node = get_keyword(cc_import.keywords, "includes").value
    assert isinstance(
        includes_node, ast.List
    ), "Атрибут 'includes' должен быть списком строк"

    includes = [node.value for node in includes_node.elts]  # type: ignore
    assert includes == ["internal"]

    headers_node = get_keyword(cc_import.keywords, "hdrs").value
    assert isinstance(
        headers_node, ast.List
    ), "Атрибут 'hdrs' должен быть списком строк"

    headers: list[str] = [node.value for node in headers_node.elts]  # type: ignore
    assert len(headers) > 0

    if not all(header.startswith("internal/") for header in headers):
        detail = "Было оговорено, что все `hdrs` начинаются на `internal`"
        raise AssertionError(detail)

    if not all(cpython_directory.joinpath(header).exists() for header in headers):
        detail = "Некоторые файлы из `hdrs` не существуют"
        raise AssertionError(detail)
