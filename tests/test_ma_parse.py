"""Headless tests for the .ma reader."""
import _bootstrap  # noqa: F401  (path setup)

from snap_on_clothing.core import ma_parse

SAMPLE = (_bootstrap.FIXTURES / "sample_coat.ma").read_text()


def test_statement_split_is_quote_aware():
    stmts = list(ma_parse.iter_statements('setAttr ".n" -type "string" "a;b";'))
    assert stmts == ['setAttr ".n" -type "string" "a;b"']


def test_multiline_statement_normalized():
    text = 'createNode joint\n  -n "cloth_root"\n  -p "Rig_GRP";'
    stmts = list(ma_parse.iter_statements(text))
    assert stmts == ['createNode joint -n "cloth_root" -p "Rig_GRP"']


def test_summarize_nodes_and_types():
    s = ma_parse.summarize(SAMPLE)
    assert s.has_node("cloth_info")
    assert s.has_node("cloth_root")
    assert s.node_types["cloth_info"] == "network"
    assert s.node_types["cloth_root"] == "joint"
    assert "Mesh_GRP" in s.node_names and "Ctrl_GRP" in s.node_names


def test_cloth_joints_helper():
    s = ma_parse.summarize(SAMPLE)
    joints = s.cloth_joints()
    assert "cloth_spine_01" in joints
    assert "Mesh_GRP" not in joints


def test_info_attrs_extracted():
    s = ma_parse.summarize(SAMPLE)
    assert s.info_attrs["assetName"] == "sample_coat_A"
    assert s.info_attrs["assetType"] == "coat"
    assert s.info_attrs["genHumanCompat"] == "v03, v04"


def test_escaped_quote_in_value():
    s = ma_parse.summarize(SAMPLE)
    assert s.info_attrs["author"] == 'Test "Q" Author'


def test_read_info_attrs_missing_file_is_empty():
    assert ma_parse.read_info_attrs("/no/such/file.ma") == {}
