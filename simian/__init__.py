from .ast import *
from .evaluator import *
from .lexer import *
from .objects import *
from .parser import *
from .repl import *
from .token import *

__all__ = (
    ast.__all__
    + evaluator.__all__
    + token.__all__
    + lexer.__all__
    + objects.__all__
    + parser.__all__
    + repl.__all__
)

__version__ = "0.0.1"
__author__ = "Emil Kloeden"
__license__ = "MIT"
__url__ = "https://github.com/emilkloeden/simian"
