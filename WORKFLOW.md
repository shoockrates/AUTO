# Workflow JSON Guide

`workflow.json` defines named mouse-automation workflows. When `main.py` opens,
each workflow appears as a button in the Tkinter window. Pressing a button runs
that workflow's steps from top to bottom.

## Starting the workflow launcher

Open the default `workflow.json` next to `main.py`:

```powershell
python main.py
```

The explicit equivalent is:

```powershell
python main.py --gui
```

Open a different workflow file:

```powershell
python main.py --workflow-file another-workflow.json
```

Use a different image-library directory:

```powershell
python main.py --gui --photos-dir "C:\path\to\my\photos"
```

## Windows executable

The windowed executable is built with:

```powershell
python -m pip install pyinstaller
python build.py
```

Run `python build.py` again whenever `main.py` changes. It performs a clean
rebuild, refreshes the editable files, and replaces the previous EXE.

The result is `dist\workflow.exe`. Keep these items together:

```text
dist/
  workflow.exe
  workflow.json
  photos/
```

The EXE deliberately loads `workflow.json` and `photos` from beside itself so
you can update workflows and images without rebuilding it. A windowed build
does not open a console; enable `"debug": "TRUE"` to use the diagnostics panel.

## Basic file structure

The recommended structure is an object containing a `workflows` array:

```json
{
  "debug": "FALSE",
  "workflows": [
    {
      "name": "Open calendar",
      "steps": [
        {
          "click": "calendar/button.png"
        }
      ]
    }
  ]
}
```

The root may also be the workflow array itself:

```json
[
  {
    "name": "Open calendar",
    "steps": [
      {
        "click": "calendar/button.png"
      }
    ]
  }
]
```

Each workflow requires:

- `name`: non-empty text displayed on its Tkinter button. Names must be unique,
  ignoring uppercase and lowercase differences.
- `steps`: an array of zero or more step objects. An empty workflow is valid
  and completes without moving the mouse.

The array-only root uses debug mode off. Unknown properties inside a step are
rejected, which helps catch spelling mistakes.

## Debug mode

Set `debug` once at the top of the file:

```json
"debug": "TRUE"
```

Accepted values are `"TRUE"`, `"FALSE"`, `true`, and `false`. The uppercase
string form is used in the provided file because it is easy to notice and
edit.

When debug mode is `"TRUE"`:

- The launcher displays a `DEBUG` badge and diagnostics panel.
- Every image step prints its template, search region, confidence, best score,
  and detected matches to the terminal.
- Workflow actions still move and click normally. Use `"dry_run": true` on a
  step when you want diagnostics without mouse actions.

When debug mode is `"FALSE"`, the diagnostics panel is hidden and the launcher
uses its compact layout.

## Image paths

Every step needs an image, supplied by `move`, `click`, or `image`.

Images are normally stored under the `photos` directory beside `main.py`:

```text
photos/
  save.png
  calendar/
    button.png
    12.png
```

All of these refer to the same calendar image:

```json
{ "move": "calendar/12.png" }
```

```json
{ "move": "calendar/12" }
```

```json
{ "move": "photos/calendar/12.png" }
```

An absolute image path is also accepted. If the extension is omitted, the
program tries supported image extensions, starting with `.png`.

Supported formats are PNG, JPG/JPEG, BMP, WebP, TIF, and TIFF.

## Step properties

The easiest step format uses the action as the property name:

```json
{ "move": "calendar/12.png" }
```

```json
{ "click": "save.png", "wait_after": 1 }
```

Use exactly one of `move` or `click`. All optional properties documented below
can be added to this short form.

The original expanded form remains supported:

```json
{
  "image": "save.png",
  "action": "click"
}
```

Do not mix a short action such as `move`, `click`, `double_click`, or
`right_click` with `image` or `action` in the same step.

## Available actions

### Find an image and move

```json
{ "move": "target.png" }
```

### Find an image and click

```json
{ "click": "target.png" }
```

### Find an image and double-click

```json
{ "double_click": "target.png" }
```

An optional `interval` controls the seconds between the two clicks:

```json
{ "double_click": "target.png", "interval": 0.15 }
```

### Find an image and right-click

```json
{ "right_click": "target.png" }
```

All four image actions support `delay`, `wait_after`, `confidence`, `region`,
`distance`, `shape`, `next`, `step`, `grayscale`, `duration`, `dry_run`, and
`verbose`.

### Wait

```json
{ "wait": 2 }
```

The number is the wait time in seconds. A wait can be stopped immediately with
the GUI's **Stop** button.

### Type text

```json
{ "type": "Hello world" }
```

Control the pause between characters with `interval`:

```json
{ "type": "Hello world", "interval": 0.05 }
```

PyAutoGUI's text writer is intended for keyboard characters supported by the
active keyboard layout.

### Press one key

```json
{ "press": "enter" }
```

Other examples include `"escape"`, `"tab"`, `"space"`, `"left"`, `"f5"`, and
`"volumeup"`.

### Press a hotkey

```json
{ "hotkey": ["ctrl", "s"] }
```

Keys are pressed together in array order and released in reverse order.
Another example:

```json
{ "hotkey": ["ctrl", "shift", "esc"] }
```

### Scroll

```json
{ "scroll": -5 }
```

Positive values scroll up and negative values scroll down. The exact physical
distance depends on the operating system and application.

Utility actions (`wait`, `type`, `press`, `hotkey`, and `scroll`) support
`delay` and `wait_after`. `type` and `hotkey` also support `interval`.

### `image`

- Type: string
- Required: only when using the expanded form
- Purpose: image template to find on the screen.

```json
"image": "calendar/12.png"
```

### `action`

- Type: string
- Values: `"move"`, `"click"`, or `"double_click"`
- Default: `"click"`
- Purpose: move the cursor to the detected image, optionally clicking it.

```json
"action": "move"
```

```json
"action": "click"
```

### `delay`

- Type: number, zero or greater
- Default: `0.0`
- Purpose: seconds to wait before searching for the image.

This is useful for giving another application time to open or update.

```json
"delay": 2.0
```

### `wait_after`

- Type: number, zero or greater
- Default: `0.0`
- Purpose: seconds to wait after this step finishes and before starting the
  next step.

```json
"wait_after": 0.5
```

### `confidence`

- Type: number greater than `0` and no greater than `1`
- Default: `0.88`
- Purpose: minimum image-match score.

Raise this value to avoid false matches. Lower it when a valid image is not
found because of small display, scaling, compression, or color differences.

```json
"confidence": 0.92
```

### `region`

- Type: array containing four integers
- Format: `[x, y, width, height]`
- Default: `null`, meaning the full screen
- Purpose: search only a rectangular part of the screen.

Width and height must be positive.

```json
"region": [100, 200, 800, 600]
```

`region` and `distance` cannot be used in the same step.

### `distance`

- Type: positive integer
- Default: `null`
- Purpose: search only near the cursor.

For example, this searches up to 250 pixels around the current cursor:

```json
"distance": 250
```

The search area is controlled by `shape`.

### `shape`

- Type: string
- Values: `"square"` or `"circle"`
- Default: `"square"`
- Purpose: select the search geometry when `distance` is used.

```json
"distance": 250,
"shape": "circle"
```

`shape` has no visible effect without `distance`.

### `next`

- Type: Boolean
- Default: `false`
- Purpose: choose the next occurrence when the same image appears multiple
  times.

Matches are ordered from top to bottom, then left to right. If the cursor is
already on one occurrence, the next occurrence is selected. Selection wraps
back to the first occurrence after the last one.

```json
"next": true
```

### `step`

- Type: positive integer or `null`
- Default: `null`
- Purpose: minimum center-to-center pixel distance for treating image matches
  as separate occurrences.

Normally this is calculated automatically from the template size. Set it
manually when nearby matches are incorrectly merged or one image creates
several detections.

```json
"step": 40
```

### `grayscale`

- Type: Boolean
- Default: `false`
- Purpose: compare image brightness without color.

This can help when colors change while the shape remains stable, but may also
increase false matches.

```json
"grayscale": true
```

### `duration`

- Type: number, zero or greater
- Default: `0.2`
- Purpose: seconds used to animate the cursor movement.

Use `0` for an immediate jump:

```json
"duration": 0
```

Use a larger value for a slower visible movement:

```json
"duration": 1.0
```

### `button`

- Type: string
- Values: `"left"`, `"right"`, or `"middle"`
- Default: `"left"`
- Purpose: mouse button used when `action` is `"click"`.

```json
"action": "click",
"button": "right"
```

This setting is ignored when `action` is `"move"`.

### `dry_run`

- Type: Boolean
- Default: `false`
- Purpose: find and report the selected match without moving or clicking.

```json
"dry_run": true
```

The detailed output is printed in the terminal from which the GUI was started.

### `verbose`

- Type: Boolean
- Default: `false`
- Purpose: print the search region, confidence scores, and all surviving
  matches to the terminal.

```json
"verbose": true
```

## Complete step

This example shows every supported step property:

```json
{
  "image": "calendar/12.png",
  "action": "click",
  "delay": 1.0,
  "wait_after": 0.5,
  "confidence": 0.88,
  "region": null,
  "distance": null,
  "shape": "square",
  "next": false,
  "step": null,
  "grayscale": false,
  "duration": 0.2,
  "button": "left",
  "dry_run": false,
  "verbose": false
}
```

For normal use, prefer the shorter equivalent:

```json
{
  "move": "calendar/12.png"
}
```

## Multiple workflows

Each workflow becomes a separate button:

```json
{
  "debug": "FALSE",
  "workflows": [
    {
      "name": "Move to calendar day",
      "steps": [
        {
          "move": "calendar/12.png"
        }
      ]
    },
    {
      "name": "Open and save",
      "steps": [
        {
          "click": "open.png",
          "wait_after": 1.0
        },
        {
          "click": "save.png"
        }
      ]
    }
  ]
}
```

## Example: move without clicking

```json
{
  "workflows": [
    {
      "name": "Find calendar day",
      "steps": [
        {
          "image": "calendar/12.png",
          "action": "move",
          "confidence": 0.9,
          "duration": 0.5
        }
      ]
    }
  ]
}
```

## Example: sequential clicks

```json
{
  "workflows": [
    {
      "name": "Open settings and save",
      "steps": [
        {
          "image": "settings.png",
          "action": "click",
          "wait_after": 1.0
        },
        {
          "image": "save.png",
          "action": "click",
          "wait_after": 0.5
        },
        {
          "image": "close.png",
          "action": "click"
        }
      ]
    }
  ]
}
```

## Example: search near the cursor

```json
{
  "workflows": [
    {
      "name": "Click nearby icon",
      "steps": [
        {
          "image": "icon.png",
          "action": "click",
          "distance": 300,
          "shape": "circle"
        }
      ]
    }
  ]
}
```

## Example: select repeated images

The first step moves to the first matching image. The second step searches
again and moves to the next occurrence:

```json
{
  "workflows": [
    {
      "name": "Visit two matching items",
      "steps": [
        {
          "image": "item.png",
          "action": "move"
        },
        {
          "image": "item.png",
          "action": "move",
          "next": true,
          "wait_after": 0.5
        }
      ]
    }
  ]
}
```

## Tkinter controls

- Workflow buttons run their corresponding workflows.
- **Reload** rereads the file without restarting the program.
- **Stop** requests a safe stop. It does not interrupt an
  image search or mouse movement already in progress; the runner stops before
  the next step or during `wait_after`.
- **Minimize while running** keeps the launcher from covering
  images on the screen. The window is restored after completion or failure.
- The dark diagnostics panel is visible only when top-level `debug` is enabled.

Only one workflow can run at a time. Workflow and reload buttons are disabled
while one is running.

## Execution and error behavior

For each image step, the program:

1. Waits for `delay`.
2. Resolves and loads the template image.
3. Captures the full screen or configured search area.
4. Detects matching occurrences at or above `confidence`.
5. Chooses the first or next occurrence.
6. Moves the cursor to the center of the chosen match.
7. Clicks when `action` is `"click"` and `dry_run` is `false`.
8. Waits for `wait_after`.
9. Continues to the next step.

Utility steps run their keyboard, wait, or scroll action directly. Their
optional `delay` runs first and `wait_after` runs afterward.

If a step fails, the workflow stops immediately and the GUI displays the
error. Common causes include:

- Image file missing or unreadable.
- Image not visible in the selected search area.
- Confidence set too high.
- Template larger than the search area.
- Invalid JSON or unsupported step property.

## Safety

PyAutoGUI's corner fail-safe is enabled. Move the cursor forcefully into a
screen corner to abort runaway mouse automation. The GUI reports that the
fail-safe was triggered.

Test a new workflow with `"dry_run": true` before allowing it to click.
Restricting a step with `region` or `distance` can also reduce accidental
matches.

## Currently unsupported workflow actions

Workflow steps currently support image-based mouse actions, waiting, typing,
key presses, hotkeys, and scrolling. The JSON runner does not yet provide
dedicated properties for:

- Dragging.
- Conditional branches.
- Loops or repeat counts.
- Automatic retries.
- Starting external programs.

Those features would require additions to the workflow validator and runner in
`main.py`.
