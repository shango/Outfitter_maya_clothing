"""Static undefined-name check over the modules the suite cannot execute.

The Maya boundary (``core/maya_*.py``) and the in-Maya scripts under ``examples/`` import
``maya.cmds``, so CI can only ``py_compile`` them. ``py_compile`` proves the syntax parses
and nothing else - a name that does not exist compiles perfectly and raises ``NameError``
the first time an artist clicks the button, inside Maya, where nobody is watching a test
runner. Two of those had shipped when this was written:

  * ``maya_skeleton.capture_cloth_skeleton_from_rig`` returned ``len(joints)``, where
    ``joints`` was a local of a *different* function - so the Publish tab's
    'Regenerate skeleton' button did all its work, wrote the profile, then raised.
  * ``skeleton.write_skeleton`` referenced ``Path``, ``json``, ``skeleton_file`` and
    ``load_cloth_skeleton``, none of which exist in that module.

So this walks each module's AST and flags any name *read* that is not bound by some
enclosing scope, a module-level binding, or builtins. It is deliberately an
over-approximation in the safe direction: comprehensions are folded into their enclosing
function scope, and annotations are skipped (``from __future__ import annotations`` makes
them strings at runtime), so it under-reports rather than crying wolf.

Same spirit as ``test_ui_builds.py``: prove the code can survive being *run*, for the
layers the suite cannot actually run.
"""
from __future__ import annotations

import ast
import builtins
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
BUILTINS = set(dir(builtins)) | {"__file__", "__name__", "__doc__", "__builtins__"}

TARGETS = sorted(
    [*(REPO / "scripts" / "outfitter" / "core").glob("maya_*.py"),
     *(REPO / "examples").glob("*.py")]
)


class _Scope:
    def __init__(self, parent: "_Scope | None" = None) -> None:
        self.names: set[str] = set()
        self.parent = parent

    def defines(self, name: str) -> bool:
        scope: _Scope | None = self
        while scope is not None:
            if name in scope.names:
                return True
            scope = scope.parent
        return False


def _bind_target(node: ast.AST, scope: _Scope) -> None:
    """Record every name bound by an assignment/for/with/except target."""
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name):
            scope.names.add(sub.id)


SCOPE_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)


def _shallow(body: list[ast.stmt]):
    """Nodes in ``body``, yielding nested scope nodes but never descending into them."""
    stack: list[ast.AST] = list(body)
    while stack:
        node = stack.pop()
        yield node
        if isinstance(node, SCOPE_NODES):
            continue
        stack.extend(ast.iter_child_nodes(node))


def _collect_bindings(body: list[ast.stmt], scope: _Scope) -> None:
    """Names bound directly in ``body``, not descending into nested scopes."""
    for node in _shallow(body):
        # a nested def/class binds its own name here, but its body is its own scope
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                scope.names.add(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    scope.names.add(
                        alias.asname or alias.name.split(".", 1)[0])
            elif isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                targets = (node.targets if isinstance(node, ast.Assign)
                           else [node.target])
                for t in targets:
                    _bind_target(t, scope)
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                _bind_target(node.target, scope)
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                for item in node.items:
                    if item.optional_vars is not None:
                        _bind_target(item.optional_vars, scope)
            elif isinstance(node, ast.ExceptHandler) and node.name:
                scope.names.add(node.name)
            elif isinstance(node, ast.NamedExpr):
                _bind_target(node.target, scope)
            elif isinstance(node, (ast.Global, ast.Nonlocal)):
                scope.names.update(node.names)
            elif isinstance(node, comprehension_types):
                # comprehensions get their own scope in Python 3; folding their targets
                # into the enclosing function is the safe direction (fewer false alarms)
                for gen in node.generators:
                    _bind_target(gen.target, scope)
            elif isinstance(node, ast.Lambda):
                _bind_args(node.args, scope)


comprehension_types = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


def _bind_args(args: ast.arguments, scope: _Scope) -> None:
    for a in (*args.posonlyargs, *args.args, *args.kwonlyargs):
        scope.names.add(a.arg)
    for a in (args.vararg, args.kwarg):
        if a is not None:
            scope.names.add(a.arg)


def _reads(body: list[ast.stmt]) -> list[ast.Name]:
    """Name loads directly in ``body`` - nested scopes are checked separately."""
    return [n for n in _shallow(body)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)]


def _annotation_names(tree: ast.AST) -> set[int]:
    """id() of every Name node living inside an annotation (never evaluated at runtime)."""
    skip: set[int] = set()
    for node in ast.walk(tree):
        ann = []
        if isinstance(node, ast.AnnAssign):
            ann = [node.annotation]
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            ann = [a.annotation for a in
                   (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs,
                    *(x for x in (node.args.vararg, node.args.kwarg) if x))
                   if a.annotation is not None]
            if node.returns is not None:
                ann.append(node.returns)
        for a in ann:
            for sub in ast.walk(a):
                skip.add(id(sub))
    return skip


def _check(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    skip = _annotation_names(tree)

    module = _Scope()
    _collect_bindings(tree.body, module)

    problems: list[str] = []

    def walk_scope(node, parent: _Scope) -> None:
        scope = _Scope(parent)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _bind_args(node.args, scope)
        _collect_bindings(node.body, scope)
        for name in _reads(node.body):
            if id(name) in skip or name.id in BUILTINS:
                continue
            if not scope.defines(name.id):
                problems.append(
                    f"{path.relative_to(REPO)}:{name.lineno}: "
                    f"undefined name {name.id!r} in {node.name!r}")
        for child in _shallow(node.body):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                walk_scope(child, scope)

    for top in tree.body:
        if isinstance(top, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            walk_scope(top, module)

    for name in _reads([s for s in tree.body if not isinstance(
            s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]):
        if id(name) in skip or name.id in BUILTINS:
            continue
        if not module.defines(name.id):
            problems.append(
                f"{path.relative_to(REPO)}:{name.lineno}: "
                f"undefined name {name.id!r} at module level")
    return problems


@pytest.mark.parametrize("path", TARGETS, ids=lambda p: p.name)
def test_no_undefined_names(path: Path) -> None:
    """Every name read in these modules resolves - they cannot be import-tested."""
    problems = _check(path)
    assert not problems, (
        "name(s) that would raise NameError inside Maya:\n  " + "\n  ".join(problems))


def test_targets_found() -> None:
    """Guard the glob: silently checking nothing would be worse than not checking."""
    names = {p.name for p in TARGETS}
    assert {"maya_skeleton.py", "maya_publish.py", "maya_rigs.py"} <= names
    assert len(TARGETS) >= 6
