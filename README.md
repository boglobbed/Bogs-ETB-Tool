[![Latest Release](https://img.shields.io/github/v/release/boglobbed/Bogs-ETB-Tool?color=red&label=Download)](https://github.com/boglobbed/Bogs-ETB-Tool/releases/latest)

![ETB Launcher](Screenshot%202026-06-08%20143343.png)
![Version Switcher](Screenshot%202026-06-08%20143422.png)

# Bog's ETB Tool

A utility tool for Escape the Backrooms speedrunning. Includes a mod manager, save file deleter, version switcher, and keybind editor.

---

## Setup

1. Download the latest release zip from the [Releases Tab](https://github.com/boglobbed/Bogs-ETB-Tool/releases)
2. **Extract it to its own folder** — don't run it from inside the zip or from your Downloads folder. Put it somewhere like your Desktop or Documents
3. Run `bogs_etb_tool.exe`
4. You'll get a UAC popup asking for admin — this is needed so the tool can write to your game directory (required for version switching and mod management). Click Yes

The tool will auto-detect your ETB installation on first launch. If it can't find it, you'll be prompted to set the path manually.

---

## ETB Launcher

Manage your mods from here.

- **Launch ETB** — launches the game
- **UE4SS toggle** — installs or removes UE4SS from your game directory. UE4SS is required for Lua mods
- **UE4SS Mods button** — opens File Explorer to your UE4SS Mods folder so you can manage mods manually
- Any other mod toggles install/remove mods from your game's mods folder

---

## Save File Deleter

Deletes your ETB save files. Useful for practice runs where you need a clean slate fast.

- **Delete Saves** — immediately deletes all save files found
- **Auto Delete** — automatically deletes saves whenever a new one is detected. Good if you're doing back-to-back runs
- **Set Keybind** — bind a key or mouse button to trigger the delete without clicking
- **Remove Keybind** — clears the keybind

Save files are stored in `%LOCALAPPDATA%\EscapeTheBackrooms\Saved\SaveGames` — the tool always looks there regardless of where your game is installed.

---

## Version Switcher

Switch between different versions of ETB. Useful for running specific patches.

- Versions are stored in a `versions` folder next to the exe. You can manually move downloaded depot files to the `versions` folder and place them in subfolders with the name of the updated being added. Each version is a subfolder containing the game files for that version
- Select a version from the list and hit **Switch Version**
- The tool will close Steam, swap the files, and report when it's done
- If your game is running when you try to switch, close it first

**When updating the tool:** copy your `versions` folder from the old tool folder into the new one, otherwise the tool won't see your existing versions.

The `versions` folder is created automatically the first time you use this tab.

---

## Keybind Editor

Edit the game's keybinds directly from the tool without launching ETB.

- Shows all keybinds currently set in your `Input.ini`
- **Add Keybind** — add a new action binding
- **Edit Keybind** — modify an existing binding's key, action, or modifiers (Shift/Ctrl/Alt)
- **Delete Keybind** — remove a binding entirely

Keybinds are stored in `%LOCALAPPDATA%\EscapeTheBackrooms\Saved\Config\WindowsNoEditor\Input.ini`.

---

## Settings (gear icon)

Click the gear icon in the top right to open settings.

- **Always on Top** — keeps the tool window above all other windows
- **Ignore Mouse Cursor** — makes the tool window click-through (only works with Always on Top enabled). Lets you interact with the game while the tool is visible
- **Set Game Path** — manually set your ETB installation path if auto-detection didn't work

---

## Notes

- The tool requires admin privileges to run — this is intentional so it can write to your game directory
- Don't run the tool from your Downloads folder — extract it to its own folder first
- The tool scans all drives (C:, D:, E:, etc.) when looking for your ETB installation
- Config files like `game_path.txt` and `mods_path.txt` are created automatically next to the exe on first run
