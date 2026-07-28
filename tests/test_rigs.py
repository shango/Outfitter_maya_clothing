"""Headless tests for registered rig profiles (core.rigs).

The rig profile is what makes the tool rig-agnostic, so it is worth pinning down hard:
the bundled GenHuman profile must carry exactly the data the tool used to hard-code, a
captured profile must survive the write/read round-trip unchanged, an invalid profile must
never reach a shared library, and discovery must prefer a studio-registered rig over the
bundled one of the same id.
"""
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from outfitter import config
from outfitter.core import rigs
from outfitter.core import skeleton as sk
from outfitter.core import skin_sets


# roots=[] pins lookups to the bundled profile so a developer's own library can't
# change what these tests assert.
BUNDLED_ONLY: list = []


@pytest.fixture(scope="module")
def genhuman():
    return rigs.load_profile("genhuman", roots=BUNDLED_ONLY)


def _minimal_skeleton(*names):
    """A tiny valid skeleton: cloth_root under Rig_GRP, then ``names`` beneath it."""
    joints = [sk.JointSpec(name="cloth_root", parent="Rig_GRP")]
    joints += [sk.JointSpec(name=n, parent="cloth_root") for n in names]
    return sk.SkeletonSpec(
        root_group="Rig_GRP", root_group_rotate=(-90.0, 0.0, 0.0),
        root_joint="cloth_root", joints=tuple(joints))


def _profile(**overrides):
    """A valid minimal profile, with any field overridden for the case under test."""
    base = dict(
        rig_id="acme_biped",
        display_name="Acme Biped",
        version="v01",
        export_group="Acme_Joint_GRP",
        skeleton=_minimal_skeleton("cloth_spine_01", "cloth_head"),
        markers=("Acme_Joint_GRP",),
    )
    base.update(overrides)
    return rigs.RigProfile(**base)


# --- the bundled GenHuman profile --------------------------------------------
def test_bundled_genhuman_profile_ships_in_the_package():
    assert (rigs.bundled_rigs_dir() / "genhuman.json").is_file()


def test_bundled_profile_is_valid(genhuman):
    assert rigs.validate_profile(genhuman) == []


def test_bundled_profile_carries_the_full_skeleton(genhuman):
    # The same 89 body-derived export joints the tool used to load from cloth_skeleton.json.
    assert len(genhuman.skeleton.joints) == 89
    assert genhuman.skeleton.root_joint == "cloth_root"
    assert genhuman.skeleton.root_group_rotate == (-90.0, 0.0, 0.0)


def test_bundled_profile_keeps_the_hard_coded_rig_identity(genhuman):
    # These moved out of config; the profile must reproduce them exactly or an existing
    # scene would stop being recognised as GenHuman.
    assert genhuman.export_group == config.EXPORT_SKELETON_GROUP
    assert genhuman.markers == config.RIG_MARKERS
    assert genhuman.label == "GenHuman v03"


def test_bundled_profile_reproduces_the_gender_morph_switch(genhuman):
    variants = genhuman.variants
    assert variants.mode == rigs.VARIANT_MORPH
    assert variants.node == config.BODY_MORPH_NODE
    assert variants.attr == config.BODY_MORPH_ATTR
    assert variants.is_gendered
    assert set(variants.names) == set(config.GENDERS)
    assert variants.value_for("male") == config.GENDER_BODY_MORPH["male"]
    assert variants.value_for("female") == config.GENDER_BODY_MORPH["female"]


def test_bundled_profile_reproduces_the_recommended_skin_sets(genhuman):
    # The per-type sets were a hard-coded table; the profile must carry them verbatim.
    for asset_type in config.ASSET_TYPES:
        assert genhuman.skin_set(asset_type) == skin_sets.genhuman_seed_joints(asset_type)


def test_bundled_profile_points_at_the_packaged_rig_file(genhuman):
    # GenHuman is the one rig that ships inside the package rather than the library.
    assert genhuman.rig_file == ""
    bundled = rigs.bundled_rig_file(genhuman)
    assert bundled is not None and bundled.name == config.BUNDLED_GENHUMAN_FILE


# --- serialization round-trip -------------------------------------------------
def test_profile_round_trips_through_json(genhuman):
    reloaded = rigs.from_json_dict(rigs.to_json_dict(genhuman))
    # `source` records where a profile was read from, not what the rig is.
    assert reloaded == rigs.RigProfile(**{**genhuman.__dict__, "source": None})


def test_write_then_load_preserves_every_field(tmp_path):
    profile = _profile(
        variants=rigs.Variants(mode=rigs.VARIANT_FILES,
                               files={"male": "_rigs/acme_biped/acme_m.ma",
                                      "female": "_rigs/acme_biped/acme_f.ma"}),
        skin_sets={"hat": ("cloth_head",)},
        joint_aliases={"cloth_GM_foot_r": "cloth_foot_r"},
        rig_file="_rigs/acme_biped/acme_v01.ma",
        author="rigger", created="2026-07-27",
    )
    rigs.write_profile(profile, rigs.library_rigs_dir(tmp_path))
    loaded = rigs.load_profile("acme_biped", roots=[tmp_path])

    assert loaded.display_name == "Acme Biped"
    assert loaded.version == "v01"
    assert loaded.export_group == "Acme_Joint_GRP"
    assert loaded.markers == ("Acme_Joint_GRP",)
    assert loaded.skeleton == profile.skeleton
    assert loaded.variants.mode == rigs.VARIANT_FILES
    assert loaded.variants.names == ("male", "female")
    assert loaded.skin_set("hat") == ("cloth_head",)
    assert loaded.joint_aliases == {"cloth_GM_foot_r": "cloth_foot_r"}
    assert loaded.rig_file == "_rigs/acme_biped/acme_v01.ma"
    assert loaded.source is not None


def test_written_profile_is_readable_json(tmp_path):
    path = rigs.write_profile(_profile(), tmp_path)
    data = json.loads(path.read_text())
    assert data["rigId"] == "acme_biped"
    assert "_comment" in data  # so someone opening the file knows what wrote it
    assert path.name == "acme_biped.json"


# --- validation ---------------------------------------------------------------
def test_valid_profile_has_no_errors():
    assert rigs.validate_profile(_profile()) == []


@pytest.mark.parametrize("field,value,fragment", [
    ("rig_id", "", "rigId"),
    ("rig_id", "Acme Biped", "safe id"),
    ("display_name", "", "displayName"),
    ("version", "", "version"),
    ("export_group", "", "exportGroup"),
    ("markers", (), "markers"),
])
def test_validation_catches_missing_identity(field, value, fragment):
    errors = rigs.validate_profile(_profile(**{field: value}))
    assert any(fragment in e for e in errors), errors


def test_validation_catches_an_empty_skeleton():
    empty = sk.SkeletonSpec(root_group="Rig_GRP", root_group_rotate=(0.0, 0.0, 0.0),
                            root_joint="cloth_root", joints=())
    errors = rigs.validate_profile(_profile(skeleton=empty))
    assert any("no joints" in e for e in errors), errors


def test_validation_catches_a_broken_skeleton_hierarchy():
    broken = sk.SkeletonSpec(
        root_group="Rig_GRP", root_group_rotate=(0.0, 0.0, 0.0), root_joint="cloth_root",
        joints=(sk.JointSpec(name="cloth_root", parent="Rig_GRP"),
                sk.JointSpec(name="cloth_x", parent="cloth_missing")))
    errors = rigs.validate_profile(_profile(skeleton=broken))
    assert any("not defined before it" in e for e in errors), errors


def test_validation_catches_a_morph_switch_with_no_attribute():
    errors = rigs.validate_profile(
        _profile(variants=rigs.Variants(mode=rigs.VARIANT_MORPH, node="godnode")))
    assert any("'attr'" in e for e in errors), errors
    assert any("variant -> value" in e for e in errors), errors


def test_validation_catches_an_unknown_variant_mode():
    errors = rigs.validate_profile(_profile(variants=rigs.Variants(mode="sometimes")))
    assert any("variants.mode" in e for e in errors), errors


def test_validation_catches_skin_set_joints_that_are_not_in_the_skeleton():
    # The exact failure a bad heuristic or a stale hand-edit would produce: the skin set
    # names a joint the rig does not have, so 'Create cloth skeleton' would select nothing.
    errors = rigs.validate_profile(_profile(skin_sets={"hat": ("cloth_not_a_joint",)}))
    assert any("not in this rig's skeleton" in e for e in errors), errors


def test_validation_catches_an_unknown_asset_type_in_skin_sets():
    errors = rigs.validate_profile(_profile(skin_sets={"spacesuit": ()}))
    assert any("unknown asset type" in e for e in errors), errors


def test_validation_rejects_an_absolute_rig_file():
    # Rig files must be library-relative or they can't resolve on another artist's machine.
    errors = rigs.validate_profile(_profile(rig_file="/mnt/local/only/acme.ma"))
    assert any("library-relative" in e for e in errors), errors


def test_validation_rejects_a_rig_file_outside_the_rigs_folder():
    errors = rigs.validate_profile(_profile(rig_file="somewhere/acme.ma"))
    assert any(rigs.RIGS_DIRNAME in e for e in errors), errors


def test_write_refuses_an_invalid_profile(tmp_path):
    with pytest.raises(ValueError):
        rigs.write_profile(_profile(version=""), tmp_path)
    assert not (tmp_path / "acme_biped.json").exists()


# --- discovery ----------------------------------------------------------------
def test_list_profiles_includes_the_bundled_rig():
    ids = [p.rig_id for p in rigs.list_profiles(roots=BUNDLED_ONLY)]
    assert ids == ["genhuman"]


def test_a_library_profile_overrides_the_bundled_one_of_the_same_id(tmp_path):
    # A studio revising the shipped GenHuman profile must win over the packaged copy.
    rigs.write_profile(_profile(rig_id="genhuman", display_name="GenHuman (studio)",
                                version="v99"),
                       rigs.library_rigs_dir(tmp_path))
    loaded = rigs.load_profile("genhuman", roots=[tmp_path])
    assert loaded.display_name == "GenHuman (studio)"
    assert loaded.version == "v99"
    # and it appears once, not twice
    assert [p.rig_id for p in rigs.list_profiles(roots=[tmp_path])] == ["genhuman"]


def test_list_profiles_sorts_by_label(tmp_path):
    rig_dir = rigs.library_rigs_dir(tmp_path)
    rigs.write_profile(_profile(rig_id="zeta", display_name="Zeta"), rig_dir)
    rigs.write_profile(_profile(rig_id="alpha", display_name="Alpha"), rig_dir)
    ids = [p.rig_id for p in rigs.list_profiles(roots=[tmp_path])]
    assert ids == ["alpha", "genhuman", "zeta"]


def test_list_profiles_skips_unreadable_files(tmp_path):
    # A half-written or stray file in a shared _rigs folder must not hide the good rigs.
    rig_dir = rigs.library_rigs_dir(tmp_path)
    rigs.write_profile(_profile(), rig_dir)
    (rig_dir / "broken.json").write_text("{not json")
    (rig_dir / "notarig.json").write_text('{"hello": "world"}')
    ids = [p.rig_id for p in rigs.list_profiles(roots=[tmp_path])]
    assert ids == ["acme_biped", "genhuman"]


def test_load_profile_raises_for_an_unknown_rig():
    with pytest.raises(LookupError) as exc:
        rigs.load_profile("nope", roots=BUNDLED_ONLY)
    assert "genhuman" in str(exc.value)  # tells the user what *is* registered


def test_find_profile_returns_none_instead_of_raising():
    assert rigs.find_profile("nope", roots=BUNDLED_ONLY) is None


def test_resolve_profile_prefers_the_requested_rig(tmp_path):
    rigs.write_profile(_profile(), rigs.library_rigs_dir(tmp_path))
    assert rigs.resolve_profile("acme_biped", roots=[tmp_path]).rig_id == "acme_biped"


def test_resolve_profile_falls_back_to_the_default_rig(tmp_path):
    rigs.write_profile(_profile(), rigs.library_rigs_dir(tmp_path))
    # an unknown/blank choice degrades to genhuman rather than erroring
    assert rigs.resolve_profile("gone", roots=[tmp_path]).rig_id == "genhuman"
    assert rigs.resolve_profile(None, roots=[tmp_path]).rig_id == "genhuman"


def test_resolve_profile_falls_back_to_any_registered_rig(tmp_path):
    # No genhuman available at all: take the first registered rig rather than nothing.
    rigs.write_profile(_profile(), rigs.library_rigs_dir(tmp_path))
    monkey_roots = [tmp_path]
    original = rigs.bundled_rigs_dir
    rigs.bundled_rigs_dir = lambda: tmp_path / "no_such_dir"
    try:
        assert rigs.resolve_profile("gone", roots=monkey_roots).rig_id == "acme_biped"
    finally:
        rigs.bundled_rigs_dir = original


def test_resolve_profile_returns_none_when_nothing_is_registered(tmp_path):
    original = rigs.bundled_rigs_dir
    rigs.bundled_rigs_dir = lambda: tmp_path / "no_such_dir"
    try:
        assert rigs.resolve_profile(None, roots=[tmp_path]) is None
    finally:
        rigs.bundled_rigs_dir = original


# --- rig id sanitizing --------------------------------------------------------
@pytest.mark.parametrize("raw,expected", [
    ("GenHuman", "genhuman"),
    ("Acme Biped", "acme_biped"),
    ("  Acme--Biped  ", "acme_biped"),
    ("v2 Rig!", "v2_rig"),
    ("2026rig", "_2026rig"),
    ("", "rig"),
    ("!!!", "rig"),
])
def test_sanitize_rig_id(raw, expected):
    assert rigs.sanitize_rig_id(raw) == expected


# --- rig file location --------------------------------------------------------
def test_rig_file_resolves_against_a_root(tmp_path):
    profile = _profile(rig_file="_rigs/acme_biped/acme_v01.ma")
    assert rigs.rig_file_path(profile, tmp_path) == tmp_path / "_rigs/acme_biped/acme_v01.ma"


def test_rig_file_is_none_without_a_root_or_a_file():
    assert rigs.rig_file_path(_profile(rig_file="_rigs/a/b.ma"), None) is None
    assert rigs.rig_file_path(_profile(), "/anywhere") is None


def test_variant_file_resolves_per_variant(tmp_path):
    profile = _profile(
        rig_file="_rigs/acme_biped/acme_v01.ma",
        variants=rigs.Variants(mode=rigs.VARIANT_FILES,
                               files={"male": "_rigs/acme_biped/acme_m.ma"}))
    assert rigs.variant_file_path(profile, "male", tmp_path).name == "acme_m.ma"
    # a variant with no file of its own falls back to the rig's single file
    assert rigs.variant_file_path(profile, "female", tmp_path).name == "acme_v01.ma"


# --- fetching a rig body on demand --------------------------------------------
def _library_profile(tmp_path, **overrides):
    """A profile whose rig body lives in the library (not bundled), written to _rigs."""
    profile = _profile(rig_file="_rigs/acme_biped/acme_v01.ma", **overrides)
    rigs.write_profile(profile, rigs.library_rigs_dir(tmp_path))
    return profile


def _place_rig(root, text="a very large rig"):
    path = root / "_rigs" / "acme_biped" / "acme_v01.ma"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_status_reports_bundled_for_genhuman(genhuman, tmp_path):
    # The packaged GenHuman only reads as 'bundled' when the .ma is actually installed;
    # a fresh checkout has no rig binaries, and then there is nothing to fetch either.
    expected = (rigs.STATUS_BUNDLED
                if rigs.bundled_rig_file(genhuman).is_file() else rigs.STATUS_NO_FILE)
    assert rigs.rig_file_status(genhuman, tmp_path, tmp_path) == expected


def test_status_remote_only_before_the_first_fetch(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    profile = _library_profile(remote)
    _place_rig(remote)
    local.mkdir()
    assert rigs.rig_file_status(profile, local, remote) == rigs.STATUS_REMOTE_ONLY


def test_status_local_after_fetching(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    profile = _library_profile(remote)
    _place_rig(remote)
    rigs.ensure_rig_file(profile, local, remote)
    assert rigs.rig_file_status(profile, local, remote) == rigs.STATUS_LOCAL


def test_status_missing_when_nobody_uploaded_the_rig(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    profile = _library_profile(remote)
    assert rigs.rig_file_status(profile, local, remote) == rigs.STATUS_MISSING


def test_status_no_file_when_the_rig_declares_none(tmp_path):
    assert rigs.rig_file_status(_profile(), tmp_path, tmp_path) == rigs.STATUS_NO_FILE


def test_ensure_copies_the_rig_down_once(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    profile = _library_profile(remote)
    source = _place_rig(remote)

    fetched = rigs.ensure_rig_file(profile, local, remote)

    assert fetched == local / "_rigs" / "acme_biped" / "acme_v01.ma"
    assert fetched.read_text() == source.read_text()


def test_ensure_does_not_recopy_an_already_fetched_rig(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    profile = _library_profile(remote)
    _place_rig(remote)
    fetched = rigs.ensure_rig_file(profile, local, remote)
    fetched.write_text("locally modified")

    again = rigs.ensure_rig_file(profile, local, remote)

    assert again.read_text() == "locally modified"  # no second copy


def test_ensure_reports_progress(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    profile = _library_profile(remote)
    _place_rig(remote, "x" * (10 * 1024 * 1024))  # 10 MB, several chunks
    seen = []

    rigs.ensure_rig_file(profile, local, remote,
                        progress=lambda done, total: seen.append((done, total)))

    assert len(seen) > 1                       # enough updates to drive a bar
    assert seen[-1][0] == seen[-1][1]          # finishes at 100%


def test_ensure_leaves_no_partial_file_when_the_copy_fails(tmp_path):
    """A truncated rig left behind would read as 'local' forever and load a broken body."""
    local, remote = tmp_path / "local", tmp_path / "remote"
    profile = _library_profile(remote)
    _place_rig(remote, "x" * (8 * 1024 * 1024))

    def explode(done, total):
        raise KeyboardInterrupt("user cancelled mid-fetch")

    with pytest.raises(KeyboardInterrupt):
        rigs.ensure_rig_file(profile, local, remote, progress=explode)

    rig_dir = local / "_rigs" / "acme_biped"
    assert not (rig_dir / "acme_v01.ma").exists()
    assert list(rig_dir.glob("*.part")) == []
    assert rigs.rig_file_status(profile, local, remote) == rigs.STATUS_REMOTE_ONLY


def test_ensure_uses_the_bundled_file_without_touching_the_library(genhuman, tmp_path):
    if not rigs.bundled_rig_file(genhuman).is_file():
        pytest.skip("bundled GenHuman rig not installed in this checkout")
    assert rigs.ensure_rig_file(genhuman, tmp_path, tmp_path) == rigs.bundled_rig_file(genhuman)


def test_ensure_explains_a_rig_with_no_registered_file(tmp_path):
    with pytest.raises(FileNotFoundError) as exc:
        rigs.ensure_rig_file(_profile(), tmp_path, tmp_path)
    assert "no rig file registered" in str(exc.value)


def test_ensure_explains_a_missing_remote_library(tmp_path):
    profile = _library_profile(tmp_path)
    with pytest.raises(FileNotFoundError) as exc:
        rigs.ensure_rig_file(profile, tmp_path / "local", None)
    assert "no remote library is configured" in str(exc.value).lower()


def test_ensure_explains_a_rig_never_uploaded(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    remote.mkdir()
    profile = _library_profile(remote)
    with pytest.raises(FileNotFoundError) as exc:
        rigs.ensure_rig_file(profile, local, remote)
    assert "register it again" in str(exc.value)


def test_ensure_fetches_the_right_variant_file(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    profile = _profile(
        rig_file="_rigs/acme_biped/acme_v01.ma",
        variants=rigs.Variants(mode=rigs.VARIANT_FILES,
                               files={"male": "_rigs/acme_biped/acme_m.ma",
                                      "female": "_rigs/acme_biped/acme_f.ma"}))
    rigs.write_profile(profile, rigs.library_rigs_dir(remote))
    for name, body in (("acme_m.ma", "male body"), ("acme_f.ma", "female body")):
        path = remote / "_rigs" / "acme_biped" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)

    fetched = rigs.ensure_rig_file(profile, local, remote, variant="female")

    assert fetched.name == "acme_f.ma"
    assert fetched.read_text() == "female body"
    # the male body was not dragged down alongside it
    assert not (local / "_rigs" / "acme_biped" / "acme_m.ma").exists()


# --- installing a rig into the rig repo (registration) ------------------------
def test_rig_file_rel_is_the_slot_the_fetcher_looks_in():
    rel = rigs.rig_file_rel("acme_biped", "acme_v01.ma")

    assert rel == "_rigs/acme_biped/acme_v01.ma"
    # the two halves of the contract agree: what registration writes is what a fetch reads
    profile = _profile(rig_file=rel)
    assert rigs.rig_file_path(profile, "/lib") == Path("/lib/_rigs/acme_biped/acme_v01.ma")


def test_install_copies_the_rig_into_the_repo_and_returns_a_relative_path(tmp_path):
    source = tmp_path / "inbox" / "acme_v01.ma"
    source.parent.mkdir()
    source.write_text("a very large rig")
    remote = tmp_path / "remote"

    rel = rigs.install_rig_file("acme_biped", source, remote)

    assert rel == "_rigs/acme_biped/acme_v01.ma"
    assert (remote / rel).read_text() == "a very large rig"


def test_installed_rig_is_immediately_fetchable(tmp_path):
    # end to end: register on the remote, then another artist's local fetch finds it.
    source = tmp_path / "acme_v01.ma"
    source.write_text("a very large rig")
    local, remote = tmp_path / "local", tmp_path / "remote"

    rel = rigs.install_rig_file("acme_biped", source, remote)
    profile = _profile(rig_file=rel)

    assert rigs.rig_file_status(profile, local, remote) == rigs.STATUS_REMOTE_ONLY
    assert rigs.ensure_rig_file(profile, local, remote).read_text() == "a very large rig"


def test_install_reports_progress(tmp_path):
    source = tmp_path / "acme_v01.ma"
    source.write_bytes(b"x" * 1000)
    seen = []

    rigs.install_rig_file("acme_biped", source, tmp_path / "remote",
                          progress=lambda done, total: seen.append((done, total)))

    assert seen[-1] == (1000, 1000)


def test_installing_a_rig_onto_itself_is_a_no_op(tmp_path):
    # re-registering a rig to fix its profile must not need the .ma to move.
    dest = tmp_path / "remote" / "_rigs" / "acme_biped" / "acme_v01.ma"
    dest.parent.mkdir(parents=True)
    dest.write_text("a very large rig")

    rel = rigs.install_rig_file("acme_biped", dest, tmp_path / "remote")

    assert rel == "_rigs/acme_biped/acme_v01.ma"
    assert dest.read_text() == "a very large rig"


def test_install_explains_a_missing_source(tmp_path):
    with pytest.raises(FileNotFoundError, match="Rig file not found"):
        rigs.install_rig_file("acme_biped", tmp_path / "nope.ma", tmp_path)


def test_install_leaves_no_partial_file_when_the_copy_fails(tmp_path):
    source = tmp_path / "acme_v01.ma"
    source.write_bytes(b"x" * 1000)
    remote = tmp_path / "remote"

    def boom(done, total):
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        rigs.install_rig_file("acme_biped", source, remote, progress=boom)

    assert list((remote / "_rigs" / "acme_biped").iterdir()) == []


# --- variant-switch name heuristic (drives the Register dialog's prefill) ------
@pytest.mark.parametrize("attr", [
    "GH_Body_morph",       # GenHuman's own switch
    "gender", "Gender", "sex", "bodyType", "body_shape",
    "maleFemaleBlend",
])
def test_variant_attr_names_are_recognised(attr):
    assert rigs.looks_like_variant_attr(attr)


@pytest.mark.parametrize("attr", [
    "translateX", "ikFkBlend", "stretch", "squashScale", "visibility",
])
def test_ordinary_control_attrs_are_not_mistaken_for_a_variant_switch(attr):
    assert not rigs.looks_like_variant_attr(attr)
