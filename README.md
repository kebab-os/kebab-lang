<div align="center">
  <img src="static/favicon.png" width="200px" height="auto" />
  <h1>kebab-lang</h1>
  <b>Kebab based scripting language</b>
</div>


## Description

**kebab** is a fun, skewered programming language — a random little language
where variables are *skewered*, loops *grill*, functions *wrap*, and output is
*served* hot.

## Quick start

```sh
# run a kebab program
python bin/kebab examples/hello.kb

# or, after pip install -e .
kebab examples/hello.kb
```

## Language reference

### Comments

```kebab
# this is a comment
// this is also a comment
```

### Printing — `serve`

```kebab
serve "Hello, World!";
serve 42;
serve 3.14;
serve true;
```

### Variables — `skewer`

Declare a variable (and assign a value) with `skewer`.
Re-assign an existing variable by writing just `name = value;`.

```kebab
skewer name = "kebab";
skewer count = 0;
count = count + 1;
```

### Data types

| Type    | Examples                |
|---------|-------------------------|
| number  | `42`, `3.14`, `-7`      |
| string  | `"hello"`, `'world'`    |
| boolean | `true`, `false`         |
| null    | `null`                  |

### Operators

| Category    | Operators                          |
|-------------|-------------------------------------|
| Arithmetic  | `+`, `-`, `*`, `/`, `%`            |
| Comparison  | `==`, `!=`, `<`, `<=`, `>`, `>=`   |
| Logical     | `and`, `or`, `not`                 |
| Concatenate | `+` (when either side is a string) |

### Conditionals — `if` / `else`

```kebab
if (x > 10) {
  serve "spicy!";
} else {
  serve "mild.";
}
```

### Loops — `grill`

```kebab
skewer i = 0;
grill (i < 5) {
  serve i;
  i = i + 1;
}
```

### Functions — `wrap` / `return`

```kebab
wrap greet(name) {
  serve "Hello, " + name + "!";
}

wrap factorial(n) {
  if (n <= 1) { return 1; }
  return n * factorial(n - 1);
}

greet("World");
serve factorial(6);  # 720
```

### Random numbers — `random(n)`

`random(n)` returns a random integer in the range `[0, n)`.

```kebab
skewer roll = random(6) + 1;  # 1–6
serve "You rolled: " + roll;
```

---

## Examples

| File | Description |
|------|-------------|
| [`examples/hello.kb`](examples/hello.kb) | Hello, World |
| [`examples/fizzbuzz.kb`](examples/fizzbuzz.kb) | Classic FizzBuzz |
| [`examples/functions.kb`](examples/functions.kb) | Functions and recursion |
| [`examples/random.kb`](examples/random.kb) | Random numbers |

---

## Running the tests

```sh
pip install pytest
python -m pytest
```

---

## Project layout

```
kebab-lang/
├── bin/kebab          # CLI entry point
├── kebab/             # interpreter package
│   ├── __init__.py    # public run() API
│   ├── tokens.py      # token types & keywords
│   ├── lexer.py       # tokenizer
│   ├── ast_nodes.py   # AST node dataclasses
│   ├── parser.py      # recursive-descent parser
│   ├── environment.py # scoped variable store
│   ├── interpreter.py # tree-walk interpreter
│   └── cli.py         # CLI logic
├── examples/          # example .kb programs
└── tests/             # pytest test suite
```
