# Simian

Yet another monkey-lang interpreter. Based off of Thorsten Ball's [Writing an interpreter in Go](interpreterbook.com). See also: [monkeylang.org](monkeylang.org).

## About
Don't use this, it is simply a side-project. There are much better interpretations available, again: see monkeylang.org.

This is a python port of my [go interpretation](https://github.com/emilkloeden/monkey).

Seemingly like most adaptations, this repo builds upon Thorsten's canonical version in this case by adding:
* Addtional operators and operations
* Additional builtin functions
* A module system


## Credits
* Thorsten Ball - Author of the book and the language
* Nightshade256 - Author of (prymate)[https://github.com/NightShade256/prymate], the resource I consistently turn to when stuck. Much of simian was "borrowed" directly from *prymate* thanks to the MIT license :).
* Prologic - Author of [prologic/monkey-lang](https://github.com/prologic/monkey-lang) from where I learned how to implement most of my additions to monkey-lang.
* bradford-hamilton - Author of [bradford-hamilton/monkey-lang](https://github.com/bradford-hamilton/monkey-lang), another key resource in my original go interpretation.

# Usage
```
usage: cli.py [-h] [--lex | --parse] [FILE]

positional arguments:
  FILE

optional arguments:
  -h, --help   show this help message and exit
  --lex, -l    Lex input only. Do not parse, evaluate or collect $200.
  --parse, -p  Lex and parse input. Do not evaluate.
```

# Roadmap

## Done
1. Additional operators and operations
    - modulus `// 3 % 2 = 1`
    - comments `// single line comments only`
    - boolean AND and OR `// true && false || true`
    - Array concatenation (`[1,2] + [3] // [1,2,3]`)
1. Additional Builtins
    - String functions
        - `split(string, delimiter) // Array`
    - Array functions
        - `join(array, delimiter) // String`
    - Hash functions
        - `keys(hash) // Array`
        - `values(hash) // Array`
1. Add module system 
    - uses absolute paths or paths relative to the importing file (or current working directory for interactive mode). I took this almost verbatim from [prologic's version](https://github.com/prologic/monkey-lang/). 
    - Note: importing executes the loaded module, so you should only import modules that don't have side-effects.
1. Create a standard library of monkey functions implemented in monkey (requires a working module system)
    - Array functions (map, filter, reduce)

## ToDo
1. Add more builtins and operations - ONGOING
    - Dictionary concatenation?
    - file I/O e.g `let f = open(filePath, ["r"|"w"|"a"])`
    - Variable destructuring - this would be a great way to improve import syntax i.e. `let {map, filter, reduce} = import("./stdlib/arrays.mo");`
    - Build upon our new standard library
1. Loops?
1. Sets?
1. Create a TCP Server
1. Create a Web Server
1. and - *if no one else has done this by the time we get here* - get some syntax highlighting going
1. Port to Java :-(