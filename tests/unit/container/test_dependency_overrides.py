from random import randint
from types import NoneType

import pytest

from dishka import (
    Provider,
    Scope,
    decorate,
    make_container,
    provide,
    provide_all,
)


def get_int() -> int:
    return 42


def get_float() -> float:
    return 5.2


def get_str() -> str:
    return "str"


def test_dependency_overrides_method():
    class MyProvider(Provider):
        scope = Scope.APP

        @provide
        def get_int(self) -> int:
            return 100

        @provide(dependency_overrides={"arg": int})
        def get_str(self, arg: str) -> None:
            assert isinstance(arg, int)

    container = make_container(MyProvider())

    container.get(NoneType)


def test_dependency_overrides_func():
    provider = Provider(scope=Scope.APP)

    def get_int() -> int:
        return 100

    def func(arg: str) -> None:
        assert isinstance(arg, int)

    provider.provide(get_int)
    provider.provide(func, dependency_overrides={"arg": int})

    container = make_container(provider)

    container.get(NoneType)


def test_dependency_overrides_class():
    class A:
        def __init__(self, arg: str) -> None:
            assert isinstance(arg, int)

    provider = Provider(scope=Scope.APP)
    provider.provide(get_int)
    provider.provide(A, dependency_overrides={"arg": int})

    container = make_container(provider)

    container.get(A)


# fails on `A.foo`, issue?
@pytest.mark.skip(reason="fails on `A.foo`")
def test_dependency_overrides_static_method():
    class A:
        @provide(dependency_overrides={"arg": int})
        @staticmethod
        def foo(arg: str) -> None:
            assert isinstance(arg, int)

    provider = Provider(scope=Scope.APP)
    provider.provide(get_int)
    provider.provide(A.foo, dependency_overrides={"arg": int})

    container = make_container(provider)

    container.get(NoneType)


def test_dependency_overrides_static_method_in_provider():
    class MyProvider(Provider):
        scope = Scope.APP

        @provide
        def get_int(self) -> int:
            return 100

        @provide(dependency_overrides={"arg": int})
        @staticmethod
        def foo(arg: str) -> None:
            assert isinstance(arg, int)

    container = make_container(MyProvider())

    container.get(NoneType)


# fails on `A.foo`, issue?
@pytest.mark.skip(reason="fails on `A.foo`")
def test_dependency_overrides_class_method():
    class A:
        @provide(dependency_overrides={"arg": int})
        @classmethod
        def foo(cls: type, arg: str) -> None:
            assert isinstance(arg, int)

    provider = Provider(scope=Scope.APP)
    provider.provide(get_int)
    provider.provide(A.foo, dependency_overrides={"arg": int})

    container = make_container(provider)

    container.get(NoneType)


def test_dependency_overrides_class_method_in_provider():
    class MyProvider(Provider):
        scope = Scope.APP

        @provide
        def get_int(self) -> int:
            return 100

        @provide(dependency_overrides={"arg": int})
        @classmethod
        def foo(cls: type, arg: str) -> None:
            assert isinstance(arg, int)

    container = make_container(MyProvider())

    container.get(NoneType)


# fails with non-typed builtin funcs,
# override that by dependency_overrides?
@pytest.mark.skip(reason="fail with non-typed builtins")
def test_dependency_overrides_builtin():
    provider = Provider(scope=Scope.APP)

    provider.provide(get_float)
    provide(
        randint,
        provides=int,
        dependency_overrides={"start": float, "end": float},
    )

    container = make_container(provider)

    with pytest.raises(ValueError, match="non-integer arg 1 for randrange()"):
        container.get(int)


def test_dependency_overrides_callable():
    class MyCallable:
        def __call__(self, arg: str) -> None:
            assert isinstance(arg, int)

    def get_int() -> int:
        return 100

    provider = Provider(scope=Scope.APP)
    provider.provide(get_int)
    provider.provide(MyCallable(), dependency_overrides={"arg": int})

    container = make_container(provider)

    container.get(NoneType)


def test_dependency_overrides_provide_all_method():
    class A:
        def __init__(self, arg: str):
            assert isinstance(arg, int)

    class B:
        def __init__(self, arg: str):
            assert isinstance(arg, int)

    provider = Provider(scope=Scope.APP)
    provider.provide(get_int)
    provider.provide_all(A, B, dependency_overrides={"arg": int})

    container = make_container(provider)

    container.get(A)
    container.get(B)


def test_dependency_overrides_provide_all_func():
    class A:
        def __init__(self, arg: str):
            assert isinstance(arg, int)

    class B:
        def __init__(self, arg: str):
            assert isinstance(arg, int)

    class MyProvider(Provider):
        scope = Scope.APP

        @provide
        def get_int(self) -> int:
            return 42

        ab = provide_all(A, B, dependency_overrides={"arg": int})

    container = make_container(MyProvider())

    container.get(A)
    container.get(B)


def test_dependency_overrides_decorate_method():
    class A:
        def __init__(self, arg: str):
            self.arg = arg

    def decorator(a: A, arg: str) -> A:
        assert isinstance(arg, str)
        a.arg = arg
        return a

    provider = Provider(scope=Scope.APP)
    provider.provide(get_int)
    provider.provide(get_str)
    provider.provide(A)
    provider.decorate(decorator, dependency_overrides={"arg": int})
    decorate(decorator)

    container = make_container(provider)

    a = container.get(A)
    assert isinstance(a.arg, int)


def test_dependency_overrides_decorate_func():
    class A:
        def __init__(self, arg: str):
            self.arg = arg

    class AProvider(Provider):
        scope = Scope.APP

        @provide
        def get_str(self) -> str:
            return "str"

        a = provide(A)

    class MyProvider(Provider):
        scope = Scope.APP

        @provide
        def get_int(self) -> int:
            return 42

        @decorate(dependency_overrides={"arg": int})
        def decorator(self, a: A, arg: str) -> A:
            assert isinstance(arg, int)
            a.arg = arg
            return a

    container = make_container(AProvider(), MyProvider())

    a = container.get(A)
    assert isinstance(a.arg, int)
