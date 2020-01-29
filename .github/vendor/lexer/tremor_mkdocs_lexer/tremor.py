"""Pygments lexer for tremor-script markup."""
from pygments.lexer import RegexLexer, words
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Whitespace
import re

__all__ = ['TremorLexer']

class TremorLexer(RegexLexer):
    """RE based tremor-script lexer."""

    name = 'Tremor-Script Markup'
    filenames = [ '*.tremor' ]
    aliases = [ 'tremor' ]
    mimetypes = ['text/x-tremor-src']

    flags = re.MULTILINE | re.UNICODE

    tokens = {
      'root': [
            # Shebang
            (r'#![^[\r\n].*$', Comment.Preproc),
            # newline
            (r'\n', Whitespace),
            # ws
            (r'\s+', Whitespace),
            # comment
            (r'#(.*?)\n', Comment.Single),
            # keywords
            (r'(const|let|emit|drop|match|of|case|when|default|end|patch|insert|update|upsert|erase|merge|for|present|absent)\b', Keyword.Declaration),
            (words((
                'const', 'let', 'emit', 'drop', 'match', 'of', 'case', 'when',
                'default', 'end', 'patch', 'insert', 'update', 'upsert',
                'erase', 'merge', 'for', 'present', 'absent'), suffix=r'\b'),
             Keyword),
            # constwords
            (r'(true|false|event|null)', Keyword.Constant),
            # wordops
            (r'(and|or|not)\b', Keyword.Constant),
            # integer
            (r'\d+i', Number),
            (r'\d+\.\d*([Ee][-+]\d+)?i', Number),
            (r'\.\d+([Ee][-+]\d+)?i', Number),
            (r'\d+[Ee][-+]\d+i', Number),
            # float
            (r'\d+(\.\d+[eE][+\-]?\d+|' r'\.\d*|[eE][+\-]?\d+)', Number.Float),
            (r'\.\d+([eE][+\-]?\d+)?', Number.Float),
            # octal
            (r'0[0-7]+', Number.Oct),
            # hex
            (r'0[xX][0-9a-fA-F]+', Number.Hex),
            # decimal
            (r'(0|[1-9][0-9]*)', Number.Integer),
            # literal ident
            #(r'`[^`]*`', Name.Other),
            # string literal
            (r'"', String, 'string'),
            # test literal
            #(r'|[^`]*|', String),
            #(r'[\[\]{}(),.:;]', Punctuation),
            #(r'[+-/*%!=~=:]', Operator),
            # identifier is anything else
            (r'[^\W\d]\w*', Name.Other),
      ],
      'string': [
            (r'"', String, '#pop'),
            (r"""\\['"\\nrt]|\\x[0-7][0-9a-fA-F]|\\0"""
             r"""|\\u\{[0-9a-fA-F]{1,6}\}""", String.Escape),
            (r'[^\\"]+', String),
            (r'\\', String),
      ]
    }
