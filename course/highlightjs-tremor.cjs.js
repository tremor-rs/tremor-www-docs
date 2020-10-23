'use strict';

// Copyright 2020, The Tremor Team

function defineTremorGrammar(hljs) {
  const BRACED_SUBST = {
    className: 'subst',
    subLanguage: 'tremor',
    variants: [{
      begin: '\\{',
      end: '}'
    }],
    keywords: 'true false null this is new super',
  };

  const KEYWORDS = {
    keyword:
      'emit drop const let for match of case when default end patch insert update erase move copy present absent' +
      ' merge fn use mod recur with as intrinsic',
    meta:
      'event args state window group',
    literal:
      'false true null'
  };

  const STRING = {
    className: 'string',
    variants: [
      {
        begin: '"""',
        end: '"""',
        contains: [hljs.BACKSLASH_ESCAPE, BRACED_SUBST]
      },
      {
        begin: '"',
        end: '"',
        illegal: '\\n',
        contains: [hljs.BACKSLASH_ESCAPE, BRACED_SUBST]
      },
    ]
  };
  BRACED_SUBST.contains = [
    hljs.C_NUMBER_MODE, STRING
  ];

  var PRIMED_IDENT = {
    className: 'string',
    begin: '`', end: '`',
    contains: [hljs.BACKSLASH_ESCAPE]
  };

  var DOLLAR_IDENT = {
    className: 'meta',
    begin: '\\$[a-zA-Z0-9]+'
  };

  var SIGNIFICANT_OPERATORS = {
    className: 'built_in',
    begin: "(=>)|(~=)|~|\\|"
  };

  return {
    name: "tremor-script",
    aliases: ["tremor"],
    keywords: KEYWORDS,
    case_insensitive: true,
    contains: [
      STRING,
      PRIMED_IDENT,
      DOLLAR_IDENT,
      SIGNIFICANT_OPERATORS,
      hljs.NUMBER_MODE,
      hljs.COMMENT(
        '#+',
        '$', {
          contains: [{
            begin: '.',
            subLanguage: 'markdown',
            end: '$',
            relevance:0
          }]
        }
      ),
    ]
  };
}

// Copyright 2020, The Tremor Team

function defineTrickleGrammar(hljs) {
  const BRACED_SUBST = {
    className: 'subst',
    subLanguage: 'tremor',
    variants: [{
      begin: '\\{',
      end: '}'
    }],
    keywords: 'true false null this is new super',
  };

  const KEYWORDS = {
    keyword:
      'emit drop const let for match of case when default end patch insert update erase move copy present absent ' +
      'merge fn use mod recur with as intrinsic select create define operator script from into with group by window ' +
      'stream tumbling sliding where having set each',
    meta:
      'event args state window group and or not',
    literal:
      'false true null'
  };

  const STRING = {
    className: 'string',
    variants: [
      {
        begin: '"""',
        end: '"""',
        contains: [hljs.BACKSLASH_ESCAPE, BRACED_SUBST]
      },
      {
        begin: '"',
        end: '"',
        illegal: '\\n',
        contains: [hljs.BACKSLASH_ESCAPE, BRACED_SUBST]
      },
    ]
  };
  BRACED_SUBST.contains = [
    hljs.C_NUMBER_MODE, STRING
  ];

  var PRIMED_IDENT = {
    className: 'string',
    begin: '`', end: '`',
    contains: [hljs.BACKSLASH_ESCAPE]
  };

  var DOLLAR_IDENT = {
    className: 'meta',
    begin: '\\$[a-zA-Z0-9]+'
  };

  var SIGNIFICANT_OPERATORS = {
    className: 'built_in',
    begin: "(=>)|(~=)|~|\\|"
  };

  return {
    name: "tremor-query",
    aliases: ["trickle"],
    keywords: KEYWORDS,
    case_insensitive: true,
    contains: [
      STRING,
      PRIMED_IDENT,
      DOLLAR_IDENT,
      SIGNIFICANT_OPERATORS,
      hljs.NUMBER_MODE,
      hljs.COMMENT(
        '#+',
        '$', {
          contains: [{
            begin: '.',
            subLanguage: 'markdown',
            end: '$',
            relevance:0
          }]
        }
      ),
    ]
  };
}

// Copyright 2020, The Tremor Team

const main = {};

main.defineTremorGrammar = defineTremorGrammar;
main.defineTrickleGrammar = defineTrickleGrammar;

module.exports = main;
