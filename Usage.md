# Usage

1. Run `python3 prototype.py img.jpg -o output.png -g -k key.jpg` Once this is run, key.jpg will be your keyfile.
2. The main window will open. Click and drag to navigate, scroll to zoom, and right click to censor. At any time, `s` can save the file to `output.png` and `r` can revert back to the last saved version. `w` increases the selection size and `q` decreases it. `t` toggles between censoring and restoring censored regions.
3. Once the desired censoring has been performed and saved, close the window.
4. Open `output.png` like so: `python3 prototype.py output.png -k key.jpg`
5. Press `d` to automatically decensor or right-click and drag (like censoring) to manually decensor (it's XOR based)
6. This new image can also be saved.
