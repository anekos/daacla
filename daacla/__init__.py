
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Type, TypeVar
import re
import sqlite3


T = TypeVar('T')


@dataclass
class Meta:
    table: str
    fields: Dict[str, Type]
    key: Optional[str] = None

    @property
    def ddl(self) -> str:
        columns = []
        for name, tipe in self.fields.items():
            col = f'  {name} {_type_to_type(tipe)}'
            if name == self.key:
                col += ' PRIMARY KEY'
            columns.append(col)
        columns_part = ',\n'.join(columns)

        return f"""CREATE TABLE IF NOT EXISTS {self.table} (
{columns_part}
)"""

    @property
    def columns(self) -> str:
        return ', '.join(self.fields.keys())

    def values(self, instance) -> Tuple[Any, ...]:
        return tuple(map(lambda it: getattr(instance, it), self.fields.keys()))


def table(key: Optional[str] = None):
    def decorate(klass):
        table = _snake_case(klass.__name__)
        klass.__daacla = Meta(
            key=key,
            table=table,
            fields=klass.__annotations__
        )
        return klass
    return decorate


def _snake_case(s: str) -> str:
    return '_'.join(map(str.lower, re.findall(r'''[A-Z][a-z0-9]*''', s)))


def _is_instance_of_daacla(instance: Any) -> bool:
    return hasattr(instance, '__daacla')


def _get_meta(instance: Any) -> Meta:
    if not _is_instance_of_daacla(instance):
        raise Exception('Not a daacla instance. Use `@daacla` decorator')
    return getattr(instance, '__daacla')


def _type_to_type(t: Type) -> str:
    if t == str:
        return 'text'
    return 'integer'


@dataclass
class Daacla:
    path: Optional[str] = None

    def __post_init__(self) -> None:
        if self.path is None:
            self.path = 'daacla.sqlite'
        self._ready = False

    def prepare(self, klass) -> Meta:
        assert self.path is not None
        meta = _get_meta(klass)

        if not self._ready:
            self.connection = sqlite3.connect(self.path, isolation_level=None)
            self.connection.execute(meta.ddl)
            self._ready = True

        return meta

    def drop_table(self, klass) -> None:
        meta = self.prepare(klass)
        self.connection.execute(f'DROP TABLE IF EXISTS {meta.table}')

    def create_table(self, klass) -> None:
        meta = self.prepare(klass)
        self.connection.execute(meta.ddl)

    def insert(self, instance) -> None:
        meta = self.prepare(instance)
        place_holders = ', '.join(['?'] * len(meta.fields.keys()))
        self.connection.execute(
            f'''INSERT INTO {meta.table} ({meta.columns}) VALUES ({place_holders})''',
            meta.values(instance)
        )

    def update(self, instance, **kwargs) -> bool:
        meta = self.prepare(instance)

        if meta.key is None:
            raise Exception(f'Primary key is not defined: {meta.table}')

        for k, v in kwargs.items():
            setattr(instance, k, v)

        pairs = map(lambda kv: '='.join(kv), zip(meta.fields.keys(), ['?'] * len(meta.fields)))
        key_value = getattr(instance, meta.key)
        q = f'''UPDATE {meta.table} SET {', '.join(pairs)} WHERE {meta.key} = {key_value}'''
        cur = self.connection.execute(q, meta.values(instance))

        return cur.rowcount == 1

    def get(self, klass: Type[T], key: Any) -> Optional[T]:
        meta = _get_meta(klass)
        q = f"""SELECT {meta.columns} FROM {meta.table} WHERE {meta.key} = {key}"""
        cur = self.connection.cursor()
        for t in cur.execute(q):
            params = {}
            for k, v in zip(meta.fields.keys(), t):
                params[k] = v
            return klass(**params)  # type: ignore
        return None
