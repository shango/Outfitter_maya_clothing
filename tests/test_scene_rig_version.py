"""MayaScene.rig_version against a minimal fake ``maya.cmds`` (no Maya).

The version gate must read the rig being dressed, not whichever rig's marker turns up
first, and must not trip over a marker short name that two nodes share.
"""
import _bootstrap  # noqa: F401

from outfitter.core.scene import MayaScene

MARKERS = ("GenHuman_Joint_GRP", "GenHuman")


class _Cmds:
    """``ls``/``attributeQuery``/``getAttr`` over ``{full path: rigVersion or None}``."""

    def __init__(self, nodes):
        self.nodes = nodes

    def ls(self, pattern, long=False):
        def leaf(path):
            return path.rsplit("|", 1)[-1]
        if pattern.startswith("*:"):
            want = pattern[2:]
            return [p for p in self.nodes if ":" in leaf(p) and leaf(p).rsplit(":", 1)[1] == want]
        return [p for p in self.nodes if leaf(p) == pattern]

    def attributeQuery(self, attr, node, exists):
        matches = [p for p in self.nodes if p == node or p.rsplit("|", 1)[-1] == node]
        if len(matches) != 1:
            raise RuntimeError(f"More than one object matches name: {node}")
        return attr == "rigVersion" and self.nodes[matches[0]] is not None

    def getAttr(self, plug):
        return self.nodes[plug.rsplit(".", 1)[0]]


def _scene(nodes):
    scene = MayaScene.__new__(MayaScene)  # skip the maya.cmds import
    scene._cmds = _Cmds(nodes)
    return scene


def test_reads_the_targeted_rig_not_the_first_one_found():
    scene = _scene({"|GenHuman": "v03", "|B:GenHuman": "v04"})

    assert scene.rig_version(MARKERS, "B:GenHuman_Joint_GRP") == "v04"
    assert scene.rig_version(MARKERS, "|GenHuman_Joint_GRP") == "v03"


def test_does_not_borrow_another_rigs_version():
    scene = _scene({"|A:GenHuman": "v03", "|B:GenHuman": None})

    assert scene.rig_version(MARKERS, "|B:Rig|B:GenHuman_Joint_GRP") is None


def test_shared_marker_short_name_does_not_raise():
    scene = _scene({"|grpA|GenHuman": None, "|grpB|GenHuman": "v03"})

    assert scene.rig_version(MARKERS, "GenHuman_Joint_GRP") == "v03"


def test_finds_marker_in_a_parent_namespace():
    # A rig with a stray nested namespace (GenHuman 3.6) keeps its markers one level up.
    scene = _scene({"|top:GenHuman": "v03", "|other:GenHuman": "v99"})

    assert scene.rig_version(MARKERS, "top:inner:GenHuman_Joint_GRP") == "v03"


def test_without_a_target_keeps_the_old_search():
    scene = _scene({"|A:GenHuman": "v03"})

    assert scene.rig_version(MARKERS) == "v03"
