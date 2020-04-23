# Functions

Tremor-script provides access to a growing number of functions that allow
advanced data manipulation or access to additional information.

Functions are namespaced to make identification easier.

Tremor also supports user defined functions. There are a few 
noteworthy restrictions:

1. Functions are pure / side effect free - you can not mutate `event`, `state`,
   or `$` inside of a function.
2. Functions have to return a value, as tremor-script is expression oriented.
3. Functions can only be defined once, even if they take different forms or
   arguments. Function overloading is not supported.
4. In matching functions, a `default` case is required.
5. Functions can call other functions but they have to be a priori defined. The order of definitions is significant.
6. Tail recursion is supported, and constrained to a maximum recursion depth. A recursion depth is imposed as tremor-script is designed to operate on infinite streams of data so indefinite blocking/recursion is not supportable by design.

Lets look at the three types of functions we have.

## Ordinary functions

Ordinary functions are functions that take a given number of arguments, each with
a name. This function can be tail- recursive. An example would be:


```tremor
## This function addds two values together
fn add(a, b) with
  a + b
end
```

## Match functions

Since matching and extracting are a core functionality for tremor matching on
function arguments is directly supported.

The same patterns that are used in `match` can be used in function cases
including extractors. If any extracting pattern is used and matches the function
argument will be replaced by the result of the extraction.


```tremor
## calculates the fibonaci sequence
fn fib_(a, b, n) of
  case (a, b, n) when n > 0 => recur(b, a + b, n - 1)
  default => a
end;

## calculates the fibonaci sequence
fn fib(n) with
  fib_(0, 1, n)
end;
```

## Var-arg functions

It is possible to use var-args for functions that do not have a simple arity. 
The variable part of the arguments is accessible via `args`. Var-arg function
can also have a set of initial known arguments.

Recursion is not possible from within var-arg functions.

```tremor
use std::array;

fn sum_(e, es) with
  let l = array::len(es);
  match l of    
    case l when l > 0 => let a = es[0], recur(e + es[0], es[1:l])
    default => e
  end
end;

fn sum(...) with
  sum_(0, args)
end
```
