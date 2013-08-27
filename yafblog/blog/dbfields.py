from sqlalchemy import types
from sqlalchemy.ext.compiler import compiles


class TSVector(types.TypeDecorator):
    impl = types.UnicodeText


@compiles(TSVector, 'postgresql')
def compile_tsvector(element, compiler, **kw):
    return 'tsvector'
