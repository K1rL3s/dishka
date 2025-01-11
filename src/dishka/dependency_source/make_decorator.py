from collections.abc import Callable
from typing import Any, overload

from dishka.text_rendering import get_name
from .composite import CompositeDependencySource, ensure_composite
from .decorator import Decorator
from .make_factory import make_factory
from .unpack_provides import unpack_decorator


def _decorate(
        source: Callable[..., Any] | type,
        provides: Any = None,
        *,
        is_in_class: bool = True,
        dependency_overrides: dict[str, type] | None = None,
) -> CompositeDependencySource:
    composite = ensure_composite(source)
    decorator = Decorator(
        make_factory(
            provides=provides,
            scope=None,
            source=source,
            cache=False,
            is_in_class=is_in_class,
            override=False,
            dependency_overrides=dependency_overrides,
        ),
    )
    if (
        decorator.provides not in decorator.factory.kw_dependencies.values()
        and decorator.provides not in decorator.factory.dependencies
    ):
        name = get_name(source, include_module=True)
        raise ValueError(
            f"Decorator {name} does not depends on provided type.\n"
            f"Did you mean @provide instead of @decorate?",
        )

    composite.dependency_sources.extend(unpack_decorator(decorator))
    return composite


@overload
def decorate(
        *,
        provides: Any = None,
        dependency_overrides: dict[str, type] | None = None,
) -> Callable[
    [Callable[..., Any]], CompositeDependencySource,
]:
    ...


@overload
def decorate(
        source: Callable[..., Any] | type,
        *,
        provides: Any = None,
        dependency_overrides: dict[str, type] | None = None,
) -> CompositeDependencySource:
    ...


def decorate(
        source: Callable[..., Any] | type | None = None,
        provides: Any = None,
        dependency_overrides: dict[str, type] | None = None,
) -> CompositeDependencySource | Callable[
    [Callable[..., Any]], CompositeDependencySource,
]:
    if source is not None:
        return _decorate(
            source,
            provides,
            is_in_class=True,
            dependency_overrides=dependency_overrides,
        )

    def scoped(func: Callable[..., Any]) -> CompositeDependencySource:
        return _decorate(
            func,
            provides,
            is_in_class=True,
            dependency_overrides=dependency_overrides,
        )

    return scoped


def decorate_on_instance(
        source: Callable[..., Any] | type,
        provides: Any = None,
        dependency_overrides: dict[str, type] | None = None,
) -> CompositeDependencySource:
    return _decorate(
        source,
        provides,
        is_in_class=False,
        dependency_overrides=dependency_overrides,
    )
