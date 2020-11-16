## Tremor Script `match`
<!-- .slide: data-background="#FF7733" -->

This tutorial introduces the `match` statement

>>>

### `match` statement

![Match rule](https://docs.tremor.rs/tremor-script/grammar/diagram/Match.png)
![Case rule](https://docs.tremor.rs/tremor-script/grammar/diagram/MatchCaseClause.png)
![Effectors rule](https://docs.tremor.rs/tremor-script/grammar/diagram/Effectors.png)
![Block rule](https://docs.tremor.rs/tremor-script/grammar/diagram/Block.png)

>>>

### `match` template

```tremor [|1-2|3-4|6-7]
match <expression> of
  # Case based pattern matching with guards
  case <pattern> when <guard> => <effectors> # Must have at least one case
  # ...
  # Default case for non-matching event data
  default => <effectors>
end
```

<div style='font-size: 20px'>
Effectors are a comma separated list of expressions
</div>

>>>

### `match` record - 1

![Record Pattern](https://docs.tremor.rs/tremor-script/grammar/diagram/RecordPattern.png)
![Array Pattern Filter](https://docs.tremor.rs/tremor-script/grammar/diagram/ArrayPatternFilter.png)

>>>

### `match` record - 2

<div style='font-size: 20px'>
Testing fields against known literal value expressions
</div>

``` tremor [|1-2|3-4|5-6|7-8]
# Is the target expression a record
case %{ } => "an empty record"
# Does the target record's field value equal the supplied expression
case %{ field == <expression> } => "a matching field value"
# Does the target record's field value not equal the supplied expression
case %{ field != <expression> } => "a non-matching field value"
# Composing multiple assertions
case %{ field == "this", field != "that" } => "value is `this` not `that`"
```

<div style='font-size: 20px'>
A record, with a field `field` with value <literal-expression>
</div>

>>>

### `match` record - 3

<div style='font-size: 20px'>
Testing for the presence or absence of a field
</div>

```tremor [|1|2]
case %{ present field } => "field `field` is present"
case %{ absent field } => "field `field` is not present"
```

<div style='font-size: 20px'>
A record, with a field  `field` present or absent
</div>

>>>

### `match` record - 5

<div style='font-size: 20px'>
Extracting matched values for further processing
</div>

```tremor [|1|2]
case matched = %{ field ~= json|{"snot": "badger" }| => }
  => matched.field.snot # "badger"
```

<div style='font-size: 20px'>
We can assign matching cases to a variable and access matched content.<br>
In the case of a json `extractor` the content is parsed into an expression.<br>
</div>

>>>

### `match` record - 6

<div style='font-size: 20px; text-align: left;'>
Problem: Pass through incoming events where they are records with an `arr` array
field containing at least one nested record, where each nested record has
a `rec` field but drop all other events and process them no further?<br>

Solution:
</div>

```tremor [|]
match event of
 case r = %{ arr ~= %[%{present rec}]} => r.arr
 default => drop   # Drop non-matching events
end
```

<div style='font-size: 20px'>
It is easier by far to express tersely as a match record pattern in `tremor-script`,
than to write in plain english!
</div>

>>>

### `match` array - 1

![Array Pattern](https://docs.tremor.rs/tremor-script/grammar/diagram/ArrayPattern.png)
![Array Pattern Filter](https://docs.tremor.rs/tremor-script/grammar/diagram/ArrayPatternFilter.png)

>>>

### `match` array - 2

``` tremor [|1|2|3|4]
case %[] => "target is an array"
case %[ ~ json|| ] => "array contains at least one json string"
case %[ ~ %[] ] => "array contains at least one nested array"
case val = %[ ~ json|| ] => { "array-of-json": val }
```

>>>

### `match` expressions

``` tremor
case 1 => "I am the integer 1"
case "string" => " I am the string `string`"
default => "I am something else
```

<div style='font-size: 20px'>
Match is not constrained to structural types. Match targets and cases can also be other values.
</div>

>>>

### `match` case guards

``` tremor
match event of
  case val = %{ present count }  when type::is_number(count) => "I am the number: { val.count }"
  default => "I do not conform"
end
```

<div style='font-size: 20px'>
Case guards allow extracted values to be further filtered for more refined matching.
</div>

>>>

### End of `match` guide
<!-- .slide: data-background="#77FF33" -->

This is the end of the `match` getting started guide

Note: This will only appear in speaker notes window


