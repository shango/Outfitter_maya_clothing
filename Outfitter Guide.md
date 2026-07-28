# Outfitter

Your one stop shop for dressing character rigs. Outfitter lets you browse a shared library
of clothing, snap a garment onto your animated character in one click, and take it off just
as cleanly. Made something new? It walks you through publishing it back to the library so
everyone can use it.

It runs as a single window inside Maya 2026, with three tabs: **Library**, **Publish**, and
**Setup**.

**GenHuman v03** comes registered out of the box. Working with a different rig? Register it
once (see *Working with rigs* below) and everything else behaves the same.

## Install and setup

Installing takes about ten seconds:

1. Drag the `install.py` file into a Maya 2026 viewport.
2. That's it. Outfitter copies itself in, drops a starter set of assets into your library,
   and adds an **Outfitter** button to your current shelf.

Click that shelf button any time to open the window.

On first run, point it at your folders on the **Setup** tab:

- **Local (working) folder:** your copy of the library. This is the only folder Outfitter
  scans.
- **Remote folder:** the shared studio library. Outfitter never writes here on its own, it
  just pulls from it.
- Click **Sync from remote** to pull the latest assets down into your local folder. It only
  ever adds and updates, and never deletes your local work.

No remote? No problem. Outfitter happily runs on just the local folder.

## Working with rigs

At the top of the **Library** and **Publish** tabs is a **Rig** dropdown. It is the answer
to "which character am I working with?", and everything else follows from it: the Library
shows you clothing for that rig, and Publish tags what you make with it. Your choice is
remembered between sessions.

**Registering a new rig.** Put the rig in a scene, go to the **Publish** tab and click
**Register rig…**. Outfitter reads the scene and proposes:

- the **export skeleton** - the group holding the joints your garments will bind to. It
  lists every candidate it found, biggest first; pick the right one, since this is the
  skeleton it captures.
- the **body variants** - the attribute that switches between male and female bodies, if
  the rig has one. Nothing in a rig says which end of the slider is which body, so if the
  two come out backwards, hit **Swap**.
- the **rig file** - the `.ma` to copy into the shared library so your colleagues can fetch
  it. Confirm it's the rig itself and not the scene you imported it into.

Click **Register** and it captures the skeleton, works out which joints each garment type
should skin to, saves the rig profile to the shared library, and selects the new rig.
Everyone else picks it up on their next **Sync**.

**Fetching a rig body.** Rig files are big, so Sync deliberately doesn't drag every one of
them onto every machine. Beside the rig dropdown you'll see where the body currently is -
*ready*, or *not downloaded* with its size. It downloads when you first need it (loading a
test body), or when you press **Fetch rig**. Just picking a rig in the dropdown never
downloads anything.

**Using a garment on a different rig.** A garment is skinned to one rig's skeleton, so it
can't simply be attached to another. Right-click it in the Library and choose **Retarget
to…**: Outfitter opens the asset, renames its joints to the new rig's, and moves them onto
the new rest pose *without disturbing your skin weights*. It shows you anything it couldn't
map before it starts.

> It does not reshape the garment. If the two rigs are different sizes the mesh will need a
> manual refit, and probably a weight touch-up. Always check the fit on the new body, then
> publish it under a new name - the original is left alone.

## Browse and attach

Open the **Library** tab to see your assets as a grid of thumbnails.

- Filter by **Gender** and **Type**, or type in the **Search** box to narrow things down.
  Clothing built for other rigs is hidden - the status line at the bottom says how many, and
  **Show other rigs** brings them into view (greyed out, since they can't be attached here).
- Click any asset to see its details on the right. The preview is a live turntable: hover
  to spin it, or drag left and right to rotate.
- **Right-click** a thumbnail for quick actions: open its folder, copy its path, or refresh
  its thumbnail.

To dress your character:

1. Make sure the rig you picked in the **Rig** dropdown is in your scene. Got several rigs
   in there? Select any node of the one you mean first.
2. Select an asset and click **Attach**. The garment snaps onto the rig and follows along as
   you pose and animate.
3. Done with it? Pick it from the **Attached** list and click **Detach**. Clean as a
   whistle, no leftovers.

The top **Refresh** button re-scans your library (and pulls from the remote first, if you
have one set up).

## Publishing a garment

Made something new? The **Publish** tab walks you through it in five numbered steps. Just
work straight down the list.

**1. Set up the cloth rig.** Check the **Rig** dropdown at the top is the rig you're
building for, pick the **Type** and **Gender**, then click **Create cloth skeleton**.
Outfitter builds that rig's cloth joints, groups your geo, and turns the joints you should
skin to green. Click **Load test body** to bring in a matching body to pose against.
(A rig with a single body has no Gender to choose, and the field says so.)

**2. Skin the mesh.** Bind your garment to those green joints (Skin > Bind Skin). A standard
smooth bind, nothing fancy.

**3. Remove the test body.** Pose the body to check your garment follows nicely, then click
**Remove test body**. (Optional: **Delete unused joints** to tidy up.)

**4. Capture the turntable.** Frame your garment in the viewport and click **Capture
turntable**. Outfitter spins around it and bakes a clean, shaded preview. Hover it to make
sure it looks good.

**5. Publish.** Fill in the details (name, version, author, and so on), click **Check scene**
to catch any problems, then hit **Publish**. Your garment lands in the shared library, ready
for everyone - tagged with the rig you built it for and the **Rig versions** it fits.

Editing something that is already published? Open it, click **Load from open scene** on the
Publish tab to fill the form automatically, make your changes, and publish again.

That is the whole tour. Now go dress some characters.
