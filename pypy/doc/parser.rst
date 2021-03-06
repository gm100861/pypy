
===========
PyPy Parser
===========

Overview
========

The PyPy parser includes a tokenizer and a recursive descent parser.

Tokenizer
---------

At the moment, the tokenizer is implemented as a single function
(``generate_tokens`` in `pypy/interpreter/pyparser/pytokenizer.py`_) that builds
a list of tokens.  The tokens are then fed to the parser.

Parser
------

The parser is a simple LL(1) parser that is similar to CPython's.

Building the Python grammar
***************************

The python grammar is built at startup from the pristine CPython grammar file
(see `pypy/interpreter/pyparser/metaparser.py`_).  The grammar builder first
represents the grammar as rules corresponding to a set of Nondeterministic
Finite Automatons (NFAs).  It then converts them to a set of Deterministic
Finite Automatons (DFAs).  The difference between a NFA and a DFA is that a NFA
may have several possible next states for any given input while a DFA may only
have one.  DFAs are therefore more limiting, but far more efficient to use in
parsing.  Finally, the assigns the grammar builder assigns each DFA state a
number and packs them into a list for the parser to use.  The final product is
an instance of the ``Grammar`` class in `pypy/interpreter/pyparser/parser.py`_.

Parser implementation
*********************

The workhorse of the parser is the ``add_token`` method of the ``Parser`` class.
It tries to find a transition from the current state to another state based on
the token it receives as a argument.  If it can't find a transition, it checks
if the current state is accepting.  If it's not, a ``ParseError`` is
raised. When parsing is done without error, the parser has built a tree of
``Node``.

Parsing Python
**************

The glue code between the tokenizer and the parser as well as extra Python
specific code is in `pypy/interpreter/pyparser/pyparse.py`_.  The
``parse_source`` method takes a string of Python code and returns the parse
tree.  It also detects the coding cookie if there is one and decodes the source.
Note that __future__ imports are handled before the parser is invoked by
manually parsing the source in `pypy/interpreter/pyparser/future.py`_.

Compiler
--------

The next step in generating Python bytecode is converting the parse tree into an
Abstract Syntax Tree (AST).

Building AST
************

Python's AST is described in `pypy/interpreter/astcompiler/tools/Python.asdl`_.
From this definition, `pypy/interpreter/astcompiler/tools/asdl_py.py`_ generates
`pypy/interpreter/astcompiler/ast.py`_, which RPython classes for the compiler
as well as bindings to application level code for the AST.  Some custom
extensions to the AST classes are in
`pypy/interpreter/astcompiler/asthelpers.py`_.

`pypy/interpreter/astcompiler/astbuilder.py`_ is responsible for converting
parse trees into AST.  It walks down the parse tree building nodes as it goes.
The result is a toplevel ``mod`` node.

AST Optimization
****************

`pypy/interpreter/astcompiler/optimize.py`_ contains the AST optimizer.  It does
constant folding of expressions, and other simple transformations like making a
load of the name "None" into a constant.

Symbol analysis
***************

Before writing bytecode, a symbol table is built in
`pypy/interpreter/astcompiler/symtable.py`_.  It determines if every name in the
source is local, implicitly global (no global declaration), explicitly global
(there's a global declaration of the name in the scope), a cell (the name in
used in nested scopes), or free (it's used in a nested function).

Bytecode generation
*******************

Bytecode is emitted in `pypy/interpreter/astcompiler/codegen.py`_.  Each
bytecode is represented temporarily by the ``Instruction`` class in
`pypy/interpreter/astcompiler/assemble.py`_.  After all bytecodes have been
emitted, it's time to build the code object.  Jump offsets and bytecode
information like the line number table and stack depth are computed.  Finally,
everything is passed to a brand new ``PyCode`` object.

.. include:: _ref.txt
