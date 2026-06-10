"""Lightweight Maya-ASCII (.ma) reader — NO maya.cmds.

The browser needs to read an asset's ``cloth_info`` metadata and do cheap
structure pre-checks *without importing the file into Maya* (PRD M1). A full
MEL/.ma parser is out of scope; we only need to:

  * split the file into statements (``...;`` terminated, quote-aware),
  * find ``createNode`` declarations and their node names,
  * read string ``setAttr`` values inside a named node block.

This is read-only and tolerant: it never raises on malformed input, it returns
best-effort results. It is NOT a validator — real validation happens in Maya
(``core.validate``, later milestone) where node typing is authoritative.

Maya ASCII shapes we rely on:
    createNode network -n "cloth_info";
        addAttr -ci true -sn "assetName" -ln "assetName" -dt "string";
    setAttr ".assetName" -type "string" "trench_coat_A";

A statement may span multiple physical lines and string values may contain
escaped quotes (``\\"``); the tokenizer below accounts for both.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

# createNode <type> -n "<name>" [-p "<parent>"] ...
_CREATE_NODE_RE = re.compile(r'^createNode\s+(\S+)\s+.*?-n\s+"((?:\\.|[^"\\])*)"')
# setAttr ".<attr>" -type "string" "<value>"   (attr may also be ".attr[0]" etc.)
_SETATTR_STR_RE = re.compile(
    r'^setAttr\b[^"]*"\.([A-Za-z_][\w.\[\]]*)"\s+-type\s+"string"\s+"((?:\\.|[^"\\])*)"'
)


def iter_statements(text: str) -> Iterator[str]:
    """Yield logical .ma statements (terminated by an unquoted ``;``).

    Newlines inside a statement are normalized to single spaces so multi-line
    ``createNode``/``setAttr`` commands match the single-line regexes above.

    ``//`` line comments (outside string literals) are stripped — Maya ASCII files
    use them as section dividers between nodes, and without stripping they would
    merge into the following statement and hide its ``createNode`` prefix. ``//``
    inside a quoted string (e.g. a path or URL in a notes attr) is preserved.
    """
    buf: list[str] = []
    in_str = False
    escaped = False
    in_comment = False
    for ch in text:
        if in_comment:
            if ch == "\n":
                in_comment = False
            continue
        if escaped:
            buf.append(ch)
            escaped = False
            continue
        if ch == "\\":
            buf.append(ch)
            escaped = True
            continue
        if ch == '"':
            in_str = not in_str
            buf.append(ch)
            continue
        if ch == "/" and not in_str and buf and buf[-1] == "/":
            buf.pop()  # drop the first '/' of the '//' comment marker
            in_comment = True
            continue
        if ch == ";" and not in_str:
            stmt = "".join(buf).strip()
            if stmt:
                yield stmt
            buf = []
            continue
        # collapse runs of whitespace (spaces/newlines/tabs) to a single space
        if ch in " \r\n\t":
            if buf and buf[-1] != " ":
                buf.append(" ")
            continue
        buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        yield tail


def _unescape(s: str) -> str:
    return s.replace('\\"', '"').replace("\\\\", "\\")


@dataclass
class MaSummary:
    """Cheap structural facts read from a .ma without loading it in Maya."""

    node_names: set[str] = field(default_factory=set)
    node_types: dict[str, str] = field(default_factory=dict)
    name_counts: dict[str, int] = field(default_factory=dict)
    info_attrs: dict[str, str] = field(default_factory=dict)
    has_references: bool = False
    has_namespaces: bool = False

    def has_node(self, name: str) -> bool:
        return name in self.node_names

    def cloth_joints(self) -> list[str]:
        from ..config import CLOTH_PREFIX

        return sorted(
            n for n in self.node_names
            if n.startswith(CLOTH_PREFIX) and self.node_types.get(n) == "joint"
        )

    def nodes_of_type(self, node_type: str) -> list[str]:
        return sorted(n for n, t in self.node_types.items() if t == node_type)

    @property
    def duplicate_names(self) -> dict[str, int]:
        """Short names declared more than once (clean assets should have none)."""
        return {n: c for n, c in self.name_counts.items() if c > 1}


def summarize(text: str, info_node: str = "cloth_info") -> MaSummary:
    """Single-pass summary of a .ma's nodes + the info node's string attrs."""
    summary = MaSummary()
    current_node: str | None = None
    for stmt in iter_statements(text):
        if stmt.startswith("createNode "):
            m = _CREATE_NODE_RE.match(stmt)
            if m:
                node_type, name = m.group(1), _unescape(m.group(2))
                summary.node_names.add(name)
                summary.node_types[name] = node_type
                summary.name_counts[name] = summary.name_counts.get(name, 0) + 1
                current_node = name
            else:
                current_node = None
            continue
        if stmt.startswith("file ") and "-r " in f" {stmt} ":
            summary.has_references = True
            continue
        if stmt.startswith("namespace ") or " -namespace " in f" {stmt} ":
            summary.has_namespaces = True
        if current_node == info_node and stmt.startswith("setAttr"):
            m = _SETATTR_STR_RE.match(stmt)
            if m:
                summary.info_attrs[m.group(1)] = _unescape(m.group(2))
    return summary


def read_info_attrs(ma_path: str | Path, info_node: str = "cloth_info") -> dict[str, str]:
    """Read string custom attrs off ``info_node``; ``{}`` if absent/unreadable."""
    try:
        text = Path(ma_path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    return summarize(text, info_node=info_node).info_attrs


def summarize_file(ma_path: str | Path, info_node: str = "cloth_info") -> MaSummary:
    try:
        text = Path(ma_path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return MaSummary()
    return summarize(text, info_node=info_node)
