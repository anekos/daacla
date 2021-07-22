
from dataclasses import dataclass
from typing import Optional

from daacla import Daacla, table


def test_daacla() -> None:
    @dataclass
    @table(key='a')
    class HogeMoge:
        a: str
        b: int
        c: Optional[bool] = None

    d = Daacla()
    d.drop_table(HogeMoge)
    d.create_table(HogeMoge)

    hoge = HogeMoge(a='a', b=1)
    d.insert(hoge)

    assert d.get(HogeMoge, key='a') == hoge

    hoge.b = 123
    assert d.update(hoge) == 1

    assert d.get(HogeMoge, key='a') == hoge

    moge = HogeMoge(a='b', b=3)
    assert d.update(moge) == 0
