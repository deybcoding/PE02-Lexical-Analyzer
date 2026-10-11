import importlib
from typing import Callable, List, Optional, Tuple

import file_io
from lexer import ERR_LEX, Token, tokenize

NEW_FILE = "New File"
OPEN_FILE = "Open File"
COMPILE_CODE = "Compile Code"
SHOW_TOKENIZED_CODE = "Show Tokenized Code"
EXIT = "Exit"

FORMATTER_MODULE = "formatter"
ERROR_MODULE = "error_diagnostics"
VARIABLE_MODULE = "variable_table"

Formatter = Callable[[List[Token]], str]
ErrorCollector = Callable[[List[Token]], List[Token]]
ErrorMessage = Callable[[Token], str]
ErrorSummary = Callable[[List[Token]], str]
VariableBuilder = Callable[[List[Token]], List[Tuple[str, str]]]


def default_format_tokens(tokens: List[Token]) -> str:
    if not tokens:
        return ""
    lines: List[List[str]] = [[] for _ in range(tokens[-1].line)]
    for t in tokens:
        lines[t.line - 1].append(t.name)
    return "\n".join(" ".join(names) for names in lines) + "\n"


def default_collect_errors(tokens: List[Token]) -> List[Token]:
    return [t for t in tokens if t.name == ERR_LEX]


def default_format_error(token: Token) -> str:
    return f"Lexical Error: Unknown word '{token.lexeme}' at line {token.line}"


def default_error_summary(tokens: List[Token]) -> str:
    count = len(default_collect_errors(tokens))
    if count == 0:
        return "No lexical errors found."
    return f"{count} lexical error(s) found."


def default_build_variable_table(tokens: List[Token]) -> List[Tuple[str, str]]:
    return []


def load_module_function(module_name: str, attr: str, fallback):
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        return fallback
    return getattr(module, attr, fallback)


class CompileResult:
    def __init__(
        self,
        tokens: List[Token],
        tokenized_code: str,
        errors: List[str],
        variables: List[Tuple[str, str]],
        tkn_path: Optional[str],
        summary: str = "",
    ):
        self.tokens: List[Token] = tokens
        self.tokenized_code: str = tokenized_code
        self.errors: List[str] = errors
        self.variables: List[Tuple[str, str]] = variables
        self.tkn_path: Optional[str] = tkn_path
        self.summary: str = summary

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    def to_dict(self) -> dict:
        return {
            "tokens": [t.to_dict() for t in self.tokens],
            "tokenized_code": self.tokenized_code,
            "errors": list(self.errors),
            "variables": list(self.variables),
            "tkn_path": self.tkn_path,
            "summary": self.summary,
        }

    def __repr__(self) -> str:
        return (
            f"CompileResult(tokens={len(self.tokens)}, errors={len(self.errors)}, "
            f"variables={len(self.variables)}, tkn_path={self.tkn_path!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CompileResult):
            return False
        return self.to_dict() == other.to_dict()


class CompilerController:
    def __init__(
        self,
        format_tokens: Optional[Formatter] = None,
        collect_errors: Optional[ErrorCollector] = None,
        format_error: Optional[ErrorMessage] = None,
        build_variable_table: Optional[VariableBuilder] = None,
        error_summary: Optional[ErrorSummary] = None,
    ):
        self.format_tokens: Formatter = format_tokens or load_module_function(
            FORMATTER_MODULE, "format_tokens", default_format_tokens
        )
        self.collect_errors: ErrorCollector = collect_errors or load_module_function(
            ERROR_MODULE, "collect_errors", default_collect_errors
        )
        self.format_error: ErrorMessage = format_error or load_module_function(
            ERROR_MODULE, "format_error", default_format_error
        )
        self.error_summary: ErrorSummary = error_summary or load_module_function(
            ERROR_MODULE, "error_summary", default_error_summary
        )
        self.build_variable_table: VariableBuilder = (
            build_variable_table
            or load_module_function(
                VARIABLE_MODULE, "build_variable_table", default_build_variable_table
            )
        )
        self.source_path: Optional[str] = None
        self.tkn_path: Optional[str] = None
        self.last_result: Optional[CompileResult] = None

    def _reset(self) -> None:
        self.tkn_path = None
        self.last_result = None

    def new_file(self) -> str:
        self.source_path = None
        self._reset()
        return ""

    def open_file(self, path: str) -> str:
        source = file_io.load_source(path)
        self.source_path = path
        self._reset()
        return source

    def save_file(self, source: str, path: Optional[str] = None) -> str:
        target = path or self.source_path
        if target is None:
            raise file_io.FileIOError("No file path to save to")
        self.source_path = file_io.save_source(target, source)
        return self.source_path

    def default_tkn_path(self) -> Optional[str]:
        if self.source_path is None:
            return None
        return file_io.token_path_for(self.source_path)

    def compile_code(
        self, source: str, tkn_path: Optional[str] = None
    ) -> CompileResult:
        tokens = tokenize(source)
        tokenized_code = self.format_tokens(tokens)
        errors = [self.format_error(t) for t in self.collect_errors(tokens)]
        summary = self.error_summary(tokens)
        variables = list(self.build_variable_table(tokens))

        target = tkn_path or self.default_tkn_path()
        self.tkn_path = file_io.save_tokens(target, tokenized_code) if target else None

        self.last_result = CompileResult(
            tokens, tokenized_code, errors, variables, self.tkn_path, summary
        )
        return self.last_result

    def show_tokenized_code(self) -> Optional[str]:
        if self.tkn_path is not None:
            return file_io.load_tokens(self.tkn_path)
        if self.last_result is not None:
            return self.last_result.tokenized_code
        return None


def compile_source(source: str, tkn_path: Optional[str] = None) -> CompileResult:
    return CompilerController().compile_code(source, tkn_path)
