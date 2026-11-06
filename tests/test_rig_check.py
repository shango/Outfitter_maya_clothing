"""Rig Check's pure rules: what each finding means and how it may be fixed."""
import _bootstrap  # noqa: F401
import pytest

from outfitter.core import rig_check as C
from outfitter.core import skin_sets

GROUP = "|Seth|Skeleton"
BODY = "|Seth|Geo|Seth_body"


def _facts(**kw):
    base = dict(group="|Seth|Seth_Joint_GRP", group_joints=89, register_default="Seth_Joint_GRP",
                rig_name="Seth")
    base.update(kw)
    return C.RigFacts(**base)


def _keys(facts):
    return [issue.key for issue in C.assemble_issues(facts)]


def _issue(facts, key):
    return next(i for i in C.assemble_issues(facts) if i.key == key)


def test_clean_rig_is_ready():
    assert C.assemble_issues(_facts()) == []
    assert C.verdict([]) == ("ok", "Ready to register.")


def test_no_rig_stops_at_one_issue():
    assert _keys(C.RigFacts()) == ["no_rig"]


@pytest.mark.parametrize("kw", [{"namespace": "ns"}, {"referenced": True}])
def test_rig_outside_its_own_file_reports_only_that(kw):
    """Fixes made to an imported or referenced rig would never reach the rig file."""
    assert _keys(_facts(renames=((GROUP, "Seth_Joint_GRP"),), **kw)) == ["not_the_rig_file"]


@pytest.mark.parametrize("scene_file, group, expected", [
    ("C:/rigs/Eric_rig_v0.6.ma", "|GenHuman|GenHuman_Joint_GRP", "Eric"),
    ("C:\\rigs\\GenHuman_Rig_3.6.ma", "|GenHuman|GenHuman_Joint_GRP", "GenHuman"),
    ("C:/rigs/scene.ma", "|Top|Jenn_Joint_GRP", "Jenn"),
    ("", "|Seth|Skeleton", "Seth"),
])
def test_guess_rig_name(scene_file, group, expected):
    assert C.guess_rig_name(scene_file, group) == expected


def test_landmark_renames_cover_every_marker():
    assert C.landmark_renames("|GenHuman|GenHuman_Joint_GRP", "|GenHuman|GenHuman_Mesh_GRP|m",
                              "Eric") == [
        ("|GenHuman|GenHuman_Joint_GRP", "Eric_Joint_GRP"),
        ("|GenHuman", "Eric"),
        ("|GenHuman|GenHuman_Mesh_GRP", "Eric_Mesh_GRP"),
        ("|GenHuman|GenHuman_Mesh_GRP|m", "Eric_body_mesh"),
    ]


def test_landmark_renames_skip_what_is_already_right():
    assert C.landmark_renames("|Seth|Skeleton", "|Seth|Geo|Seth_body_mesh", "Seth") == [
        ("|Seth|Skeleton", "Seth_Joint_GRP"), ("|Seth|Geo", "Seth_Mesh_GRP")]


def test_landmark_renames_leave_an_unrelated_top_node():
    """Jenn v1.6 sits under JENN: a fine marker, and it must not read as a blocker."""
    assert C.landmark_renames("|JENN|Jenn_Joint_GRP", "|JENN|Jenn_Mesh_GRP|Jenn_body_mesh",
                              "Jenn") == []


def test_landmark_renames_handle_a_flat_rig():
    """No top node above the group, and a body straight under the top: no invented names."""
    assert C.landmark_renames("|Skeleton", "", "Seth") == [("|Skeleton", "Seth_Joint_GRP")]
    assert C.landmark_renames("|Seth|Seth_Joint_GRP", "|Seth|body", "Seth") == [
        ("|Seth|body", "Seth_body_mesh")]


@pytest.mark.parametrize("name, ok", [("Eric", True), ("_x1", True), ("1a", False),
                                      ("a b", False), ("", False), ("a:b", False)])
def test_valid_rig_name(name, ok):
    assert C.valid_rig_name(name) is ok


def test_budget_row_keeps_heaviest_and_renormalizes():
    keep, drop = C.budget_row([(.4, 0), (.3, 1), (.1, 2), (.1, 3), (.06, 4), (.04, 5)])
    assert sorted(i for _, i in keep) == [0, 1, 2, 3]
    assert sorted(drop) == [4, 5]
    assert sum(w for w, _ in keep) == pytest.approx(1.0)
    assert dict((i, w) for w, i in keep)[0] == pytest.approx(.4 / .9)


def test_budget_row_renormalizes_an_in_budget_row():
    keep, drop = C.budget_row([(.5, 7), (.25, 9)])
    assert drop == []
    assert sum(w for w, _ in keep) == pytest.approx(1.0)


def test_budget_row_leaves_an_empty_row_alone():
    assert C.budget_row([]) == ([], [])


def test_rename_needs_the_artist_and_blocks_registration():
    issue = _issue(_facts(renames=((GROUP, "Seth_Joint_GRP"),)), "rename")
    assert (issue.level, issue.fix, issue.default) == (C.ERROR, C.FIX_INPUT, "Seth")
    assert "Skeleton -> Seth_Joint_GRP" in issue.detail


def test_renaming_a_registered_rig_warns_it_would_break():
    issue = _issue(_facts(renames=((GROUP, "x"),), registered_as="GenHuman v03"), "rename")
    assert "breaks its profile" in issue.action


def test_registered_rig_with_good_names_is_only_a_note():
    """GenHuman itself must read ready, and Eric v0.6 must still be able to take a new name."""
    issue = _issue(_facts(registered_as="GenHuman v03"), "rename")
    assert (issue.level, issue.fix, issue.default) == (C.INFO, C.FIX_INPUT, "")
    assert C.verdict([issue])[0] == "ok"


def test_taken_name_is_manual():
    issue = _issue(_facts(taken=((GROUP, "Seth_Joint_GRP"),)), "names_taken")
    assert (issue.level, issue.fix) == (C.ERROR, C.FIX_MANUAL)


def test_tied_group_replaces_the_register_default_warning():
    keys = _keys(_facts(tied_group="|Other", register_default="Other"))
    assert keys == ["tied_group"]


def test_register_default_warns_when_it_is_not_the_skinned_group():
    assert _issue(_facts(register_default="GenHuman_rig_deformLayer_hrc"),
                  "register_default").level == C.WARN


def test_settings_fix_is_safe_unless_the_method_changes():
    """maxInfluences moves nothing; skinningMethod can, so it must not be batched."""
    limits = _facts(skins=(C.SkinFacts("sc", "|m", max_influences=8, maintain_max=False),))
    assert _issue(limits, "skin_settings:sc").fix == C.FIX_SAFE
    method = _facts(skins=(C.SkinFacts("sc", "|m", method=2),))
    assert _issue(method, "skin_settings:sc").fix == C.FIX_REVIEW


def test_weight_prune_is_never_batched_and_never_blocks():
    """It overwrites the rigger's weights, and Seth keeps 10 influences by choice."""
    issue = _issue(_facts(skins=(C.SkinFacts("sc", "|m", 100, peak=10, over_budget=7),)),
                   "skin_weights:sc")
    assert (issue.level, issue.fix) == (C.WARN, C.FIX_REVIEW)


def test_only_the_body_off_bind_blocks():
    body = C.SkinFacts("body", "|b", 1000, bind_error=1.0)
    leftover = C.SkinFacts("left", "|l", 10, bind_error=6.0)
    facts = _facts(skins=(leftover, body))
    assert _issue(facts, "bind:body").level == C.ERROR
    assert _issue(facts, "bind:left").level == C.WARN


def test_bind_tolerance_ignores_float_noise():
    assert _keys(_facts(skins=(C.SkinFacts("sc", "|m", 10, bind_error=5.8e-6),))) == []


def test_unreadable_cluster_says_so():
    issue = _issue(_facts(skins=(C.SkinFacts("sc", "sc", readable=False),)), "skin_unread:sc")
    assert issue.level == C.INFO


@pytest.mark.parametrize("key, kw", [
    ("unweighted", {"unweighted_joints": ("thigh_l",)}),
    ("controls", {"controls_off_default": ("god_anim",)}),
    ("dead_switch", {"dead_switches": ("god.GH_Body_morph",)}),
    ("namespaces", {"stray_namespaces": ("bodytemp",)}),
    ("arnold", {"requires_arnold": True}),
])
def test_judgement_calls_are_never_auto_fixed(key, kw):
    assert _issue(_facts(**kw), key).fix == C.FIX_MANUAL


def test_orphans_are_safe_and_unknowns_are_reviewed():
    assert _issue(_facts(orphan_shapes=("|m|Orig1",)), "orphans").fix == C.FIX_SAFE
    assert _issue(_facts(unknown_plugins=("stereoCamera",)), "unknown").fix == C.FIX_REVIEW


def test_requires_arnold_reads_a_wrapped_requires():
    header = ['requires maya "2026";\n', 'requires -nodeType "aiOptions"\n',
              '\t\t -nodeType "aiAOVDriver" "mtoa" "5.5.3";\n', 'createNode transform;\n']
    assert C.requires_arnold(header)


def test_requires_arnold_stops_at_the_header():
    """A node body quoting the name later in the file is not a declaration."""
    assert not C.requires_arnold(['requires maya "2026";\n', 'createNode transform;\n',
                                  'setAttr ".x" -type "string" "mtoa";\n'])


def test_only_a_versioned_namespace_warns():
    """GenHuman_rig on the bundled rig is harmless; the v002 one misreads the rig version."""
    assert _issue(_facts(stray_namespaces=("GenHuman_rig",)), "namespaces").level == C.INFO
    assert _issue(_facts(stray_namespaces=("model_v002_x",)), "namespaces").level == C.WARN


def test_off_bind_title_stays_short_for_long_mesh_names():
    facts = _facts(skins=(C.SkinFacts("big", "|b", 100),
                          C.SkinFacts("left", "|" + "x" * 90, 10, bind_error=6.0)))
    assert _issue(facts, "bind:left").title == "left is off its bind pose"


def test_every_cause_and_fix_is_short():
    """The artist acts on these directly: one sentence each, data lines aside."""
    skin = C.SkinFacts("sc", "|m", 100, method=1, peak=9, over_budget=7, off_sum=2, bind_error=1)
    leftover = C.SkinFacts("left", "|l", 10, bind_error=1)
    facts = _facts(
        tied_group="|Other", profile_errors=("bad",), missing_joints=("a",), extra_joints=("b",),
        renames=((GROUP, "Seth_Joint_GRP"),), taken=((GROUP, "x"),), registered_as="GenHuman v03",
        skins=(skin, leftover, C.SkinFacts("multi", "multi", readable=False)),
        unweighted_joints=("thigh_l",), controls_off_default=("a_anim",),
        dead_switches=("god.morph",), stray_namespaces=("x_v002",), requires_arnold=True,
        orphan_shapes=("|o",), unknown_nodes=("n",))
    issues = (C.assemble_issues(facts) + C.assemble_issues(C.RigFacts())
              + C.assemble_issues(_facts(namespace="ns"))
              + C.assemble_issues(_facts(register_default="Big", registered_as="GenHuman v03")))
    assert len(issues) >= 18
    for issue in issues:
        assert len(issue.action) <= 90, issue.action
        assert len(issue.detail.splitlines()[0]) <= 100, issue.detail


def test_count_agrees_with_its_number():
    assert (C.count(1, "node"), C.count(2, "node")) == ("1 node", "2 nodes")


def test_issues_sort_most_serious_first():
    facts = _facts(unknown_nodes=("n",), orphan_shapes=("|o",), profile_errors=("bad",))
    assert [i.level for i in C.assemble_issues(facts)] == [C.ERROR, C.WARN, C.INFO]


def test_verdict_counts():
    facts = _facts(orphan_shapes=("|o",), profile_errors=("bad",))
    assert C.verdict(C.assemble_issues(facts)) == (
        C.ERROR, "Not ready to register: 1 must be fixed, 1 to review.")
    assert C.verdict(C.assemble_issues(_facts(orphan_shapes=("|o",))))[0] == C.WARN


def test_garment_joints_compare_as_bare_names():
    """The scan compares these against bare influence names, so no cloth_ may survive."""
    names = {j for js in skin_sets.derive_skin_sets(("root", "pelvis", "thigh_l")).values()
             for j in js}
    assert "thigh_l" in names
