from typing import TYPE_CHECKING, TypeAlias, Any, Generator

if TYPE_CHECKING:
    import pytest

GMonkeyPatch: TypeAlias = Generator["pytest.MonkeyPatch", Any, None]
