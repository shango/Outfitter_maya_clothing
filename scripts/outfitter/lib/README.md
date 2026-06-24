# Bundled GenHuman test body

The **"Load test body"** action on the Publish tab *references* a GenHuman rig from here,
flips `GH_Body_morph` to match the garment's chosen Gender (female = base, male = full
morph), and connects it to the `cloth_*` skeleton so the rigger can pose the body and
confirm the garment deforms before publishing. **"Remove test body"** drops that reference,
which deletes every node it brought in (selection sets included) so nothing is stranded to
block publish.

## Expected file

```
GenHuman_rig_v03.ma
```

(the name in `config.BUNDLED_GENHUMAN_FILE`). One rig serves both genders — the tool
sets the morph; it is **not** two separate files.

## Why it's not in git

The GenHuman rig is large (~27 MB) and, like the source rigs at the repo root, is kept
**out of git** (`.gitignore`). Drop the file in here for local dev, and the
package/release step includes it in the artist bundle (this `lib/` dir sits inside the
`outfitter` package, so the installer's package copytree ships it alongside the
code). If the file is missing at runtime, "Load test body" fails with a clear
"reinstall / place the rig file there" message.
