"""Audit a clothing library for damage left by two bugs fixed in 1.3.1. Read-only by default.

    python tools/library_audit.py <library folder> [<library folder> ...] [--repair]

Checks every asset in each library:

* **Wrong rig stamp** - *Stamp rig metadata* used to stamp legacy GenHuman assets with
  whichever rig was selected (see ``migrate.find_misstamped`` for the fingerprint).
  ``--repair`` points them back at GenHuman, after copying each sidecar to
  ``<name>.json.bak-<timestamp>`` beside it.
* **Unfinished retarget** - retarget used to skip renaming the children of a renamed
  joint. Such an asset has ``cloth_*`` joints named after another registered rig's
  skeleton that its own rig doesn't have. Reported only: the fix is to retarget the
  asset again (or rename those joints) in Maya.

Joints that belong to no registered rig (a garment's own helper joints) are listed
for information; they are normal.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from outfitter.core import library, ma_parse, migrate, rigs  # noqa: E402


def audit(root: Path, repair: bool) -> int:
    """Print the findings for one library; return how many need attention."""
    print(f"\n== {root}")
    if not root.is_dir():
        print("   not found")
        return 1
    profiles = {p.rig_id: p for p in rigs.list_profiles([root])}
    scan = library.scan_library([root])
    print(f"   {len(scan.assets)} asset(s), rigs: {', '.join(sorted(profiles)) or 'none'}")
    issues = 0

    sidecars = [a.sidecar for a in scan.assets if a.sidecar is not None]
    for path in migrate.find_misstamped(sidecars):
        issues += 1
        print(f"   WRONG RIG STAMP  {path.relative_to(root)}")
        if repair:
            backup = path.with_name(f"{path.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
            shutil.copy2(path, backup)
            migrate.repair_misstamped(path)
            print(f"      repaired -> genhuman (backup {backup.name})")

    for asset in scan.assets:
        rig_id = asset.metadata.rig_id if asset.metadata else rigs.DEFAULT_RIG_ID
        own = profiles.get(rig_id)
        if own is None:
            print(f"   note: {asset.ma_path.relative_to(root)} is for unregistered rig '{rig_id}'")
            continue
        joints = set(ma_parse.summarize_file(asset.ma_path).cloth_joints())
        extra = joints - set(own.joint_names)
        foreign = {j: sorted(r for r, p in profiles.items()
                             if r != rig_id and j in set(p.joint_names))
                   for j in extra}
        stale = {j: rs for j, rs in foreign.items() if rs}
        if stale:
            issues += 1
            print(f"   UNFINISHED RETARGET  {asset.ma_path.relative_to(root)} ({rig_id}): "
                  + ", ".join(f"{j} (from {'/'.join(rs)})" for j, rs in sorted(stale.items())))
        helpers = sorted(j for j, rs in foreign.items() if not rs)
        if helpers:
            print(f"   info: {asset.display_name} has {len(helpers)} helper joint(s): "
                  + ", ".join(helpers[:6]) + (" ..." if len(helpers) > 6 else ""))
    print(f"   -> {issues} issue(s)")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("libraries", nargs="+", type=Path)
    parser.add_argument("--repair", action="store_true",
                        help="fix wrong rig stamps (backing each sidecar up first)")
    args = parser.parse_args()
    total = sum(audit(root, args.repair) for root in args.libraries)
    print(f"\n{total} issue(s) in total")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
