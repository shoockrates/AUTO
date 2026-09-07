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
      "toast": "Calendar opened",
      "else": "Could not open the calendar",
      "steps": [
        {
          "click": "calendar/button.png",
          "navigate": "window-title.png",
          "toast": "Clicked the calendar button",
          "else": "Calendar button was not on the screen"
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

Every step needs an image, supplied by `move`, `click`, `find`, `navigate`,
or `image`.

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

Use exactly one of `move`, `click`, `find`, or `navigate`. All optional
properties documented below can be added to this short form.

The original expanded form remains supported:

```json
{
  "image": "save.png",
  "action": "click"
}
```

Do not mix a short action such as `move`, `click`, `double_click`,
`right_click`, `find`, or `navigate` with `image` or `action` in the same step.

`toast` and `else` can be added to any step. `navigate` can be added to an
image step as an optional on-fail handle without counting as a second action.

## Available actions

### Find an image without moving

```json
{ "find": "target.png" }
```

Use this to confirm you are on the right screen or that a control is visible.
The step succeeds if the image is found and fails if it is not. The mouse is
not moved and nothing is clicked or typed.

```json
{
  "find": "home-title.png",
  "toast": "Home screen is open",
  "else": "Home screen was not visible"
}
```

`find` supports the same optional properties as the other image actions,
including `navigate` as an on-fail handle.

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

All five image actions (`find`, `move`, `click`, `double_click`, `right_click`)
support `delay`, `wait_after`, `confidence`, `region`, `distance`, `shape`,
`next`, `step`, `grayscale`, `duration`, `dry_run`, `verbose`, `toast`, `else`,
and `navigate`. `duration` and `button` have no effect on `find`.

### Navigate to an image

```json
{ "navigate": "target.png" }
```

`navigate` is an alias for `move`. Use it when you only want the cursor to go
to the image.

The same property is also an optional on-fail handle on another image action.
See [`navigate` as a fallback](#navigate-as-a-fallback).

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

`type` uses layout-independent Unicode input by default. Text is entered
exactly as written even when the active Windows layout is Lithuanian:

```json
{ "type": "524 įčė ąęšųūž" }
```

The example above types both the digits and Lithuanian characters correctly;
it does not translate `524` into the Lithuanian number-row characters.

Control the pause between characters with `interval`:

```json
{ "type": "Hello world", "interval": 0.05 }
```

For an application that rejects Windows Unicode input and specifically needs
physical key presses, select keyboard mode:

```json
{ "type": "abc", "type_mode": "keyboard" }
```

Keyboard mode follows the active keyboard layout, so number-row keys may
produce Lithuanian characters. Supported `type_mode` values are `"unicode"`
(default) and `"keyboard"`.

### Write text (`write`)

`write` is the same action as `type`. Use it when the text is a path or
filename you want filled into a save dialog:

```json
{ "write": "{{folder}}/{{n}}.csv" }
```

This types the resolved text into the focused field. It does not create the
file by itself; the application that owns the dialog still has to save.

`{{desktop}}` and `{{home}}` are built in. Your own names come from `vars`
and `for` loops. See [Variables](#variables) and [Loops](#loops).

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

Utility actions (`wait`, `type`, `write`, `press`, `hotkey`, `scroll`, and
`toast`) support `delay` and `wait_after`. `type`, `write`, and `hotkey` also
support `interval`. All of them can include `toast`, `else`, and `optional`.

### Toast message

Show a corner notification. This can be a dedicated step:

```json
{ "toast": "Starting the import" }
```

Or a success message on any other step:

```json
{ "click": "save.png", "toast": "Saved" }
```

A dedicated toast step always succeeds and then displays the text. On an
action step, `toast` appears only after that step succeeds.

### `toast`

- Type: string
- Required: no, except when the step is a dedicated toast
- Purpose: success notification text.

```json
"toast": "Clicked the screenshot"
```

### `else`

- Type: string
- Required: no
- Purpose: failure notification text. Shown together with the technical reason
  (missing image, unreadable file, fail-safe, and similar).

```json
"else": "Could not find the Save button"
```

If a step has no `else`, the workflow-level `else` is used. If that is also
omitted, the toast shows only the technical error.

### `image`

- Type: string
- Required: only when using the expanded form
- Purpose: image template to find on the screen.

```json
"image": "calendar/12.png"
```

### `action`

- Type: string
- Values: `"find"`, `"move"`, `"click"`, or `"double_click"`
- Default: `"click"`
- Purpose: verify the image, move to it, or click it.

```json
"action": "find"
```

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

This setting is ignored when `action` is `"move"` or `"find"`.

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

## Navigate as a fallback

`navigate` is optional on `find`, `move`, `click`, `double_click`, and
`right_click`.
It is **not** run on the success path. It is only used when the primary image
is not found on screen.

When that happens, the runner:

1. Moves the cursor to the `navigate` handle image.
2. Searches for the original image once more.
3. Continues the workflow if the retry succeeds.
4. Stops and shows the `else` toast if the handle or the retry fails.

```json
{
  "click": "save.png",
  "navigate": "window-title.png",
  "toast": "Saved",
  "else": "Save was not on the screen"
}
```

Use a handle that is always visible, such as a window title, tab, or toolbar
icon. Navigating there can reveal the original control or at least move the
cursor to a known place before the retry.

`navigate` is skipped when the primary image is found on the first try. It is
also skipped for missing template files; those fail immediately because the
screenshot is not available to search with.

A standalone navigate step still means "move to this image now":

```json
{ "navigate": "window-title.png" }
```

## Try the first match that works

JSON cannot have two `"click"` keys in one object. Put alternatives in an
array. The runner tries them in order and **stops after the first success**:

```json
{
  "try": [
    { "click": "picture.png" },
    { "click": "picture_2.png" }
  ]
}
```

If `picture.png` is found, `picture_2.png` is not used. If the first click
fails, the second is tried. If every alternative fails, the workflow fails
unless the try itself is marked not needed.

```json
{
  "try": [
    { "click": "ok.png" },
    { "click": "continue.png" }
  ],
  "needed": false,
  "else": "Neither OK nor Continue was on the screen"
}
```

A try can wrap any steps, including `find`, `write`, and nested lists of
actions.

## Not-needed steps

Some UI may or may not appear. Mark those steps so a missing image does not
fail the workflow:

```json
{ "click": "cookie-banner.png", "needed": false }
```

```json
{ "find": "hint.png", "optional": true }
```

`needed: false` and `optional: true` mean the same thing: run the step if the
image is there, otherwise skip it and continue. Do not set both to
conflicting values.

Use `try` when you want one of several pictures. Use `needed: false` when
the step is extra and skipping it is fine.

## Workflow-level messages

`toast` and `else` can also sit next to `name` and `steps`:

```json
{
  "name": "Open and save",
  "toast": "Finished opening and saving",
  "else": "Open and save failed",
  "steps": [
    {
      "click": "open.png",
      "toast": "Opened"
    },
    {
      "click": "save.png",
      "else": "Could not find Save"
    }
  ]
}
```

- Workflow `toast` appears after every step succeeds.
- Step `else` is preferred over workflow `else` for the failing step.
- Failure toasts always include the technical reason under the custom text.

## Variables

Put reusable text on the workflow with `vars`. Insert a value with
`{{name}}` in image paths, typed text, toasts, and similar strings.

```json
{
  "name": "Save export",
  "vars": {
    "folder": "{{desktop}}/data",
    "name": "export"
  },
  "steps": [
    {
      "write": "{{folder}}/{{name}}.csv"
    }
  ]
}
```

Built-in names:

- `{{desktop}}` — the current user's Desktop folder
- `{{home}}` — the user profile folder
- `{{index}}` — 1-based position inside a `for` loop

A workflow `vars` object may override `desktop` or `home` if those folders
live somewhere else. Names may contain letters, digits, and `_`, and must
start with a letter or `_`.

`vars` belongs next to the workflow `name`, or on the `for` loop itself.
Do not write `{{vars}}` or `{{steps}}` — those words are JSON keys. The
placeholders are the names inside `vars` and the loop (`{{folder}}`,
`{{n}}`, `{{desktop}}`).

## Loops

`for` repeats nested `steps` once per value, substituting `{{name}}` each
time. Use it whenever the same actions would otherwise be copied 10, 31, or
100 times. The loop is not tied to a calendar; a month-length range is only
one way to produce the values.

### Numeric range

The usual form. `n` can be any name you want (`item`, `page`, `row`, …):

```json
{
  "for": {
    "n": { "from": 1, "to": 31 }
  },
  "skip_failed": true,
  "steps": [
    { "click": "item_{{n}}.png" },
    { "write": "{{folder}}/{{n}}.csv" }
  ]
}
```

`step` is optional and defaults to `1`. `"pad": 2` turns `1` into `01` when
screenshots or files use leading zeros.

A `month` object is only a shortcut for “this many days in that month”
(28–31). It is optional:

```json
{ "n": { "month": "2026_09", "pad": 2 } }
```

`month` accepts `2026_09` or `2026-09`.

### Explicit list

```json
{
  "for": {
    "name": ["alpha", "beta", "gamma"]
  },
  "steps": [
    { "write": "{{folder}}/{{name}}.csv" }
  ]
}
```

### `skip_failed`

When `true`, a failed inner step skips the rest of that iteration and
continues with the next value. Use this when some items may be missing.

When `false` (default), the first failure stops the whole workflow.

### `optional` / `needed`

On any normal step or `try` block:

```json
"needed": false
```

```json
"optional": true
```

These two forms are equivalent. The step runs if it can, and is skipped if
the image is missing (or every `try` alternative fails). The next step still
runs.

Prefer `skip_failed` on a loop when a failed item should also skip the
following steps in that same iteration.

Loops can be nested. Inner loops see outer variables.

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
  "verbose": false,
  "toast": "Clicked day 12",
  "else": "Day 12 was not visible",
  "navigate": "calendar/button.png",
  "optional": false
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

## Example: verify without clicking

```json
{
  "workflows": [
    {
      "name": "Confirm home screen",
      "steps": [
        {
          "find": "home-title.png",
          "toast": "Home screen is open",
          "else": "Home screen was not visible"
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

## Example: repeat a sequence with a variable

Same click and path-typing steps, 31 times, without copying the block:

```json
{
  "name": "Export numbered items",
  "vars": {
    "folder": "{{desktop}}/data"
  },
  "toast": "Finished {{folder}}",
  "steps": [
    {
      "for": {
        "n": { "from": 1, "to": 31 }
      },
      "skip_failed": true,
      "steps": [
        {
          "click": "item_{{n}}.png",
          "else": "Item {{n}} was not visible"
        },
        {
          "write": "{{folder}}/{{n}}.csv"
        }
      ]
    }
  ]
}
```

Change `from` / `to`, the image name, and the `write` string to match your
other program. Use a list instead of a range when the values are names
rather than numbers.

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

## Example: toasts and on-fail navigate

```json
{
  "workflows": [
    {
      "name": "Open and save",
      "toast": "Finished opening and saving",
      "else": "Open and save failed",
      "steps": [
        {
          "toast": "Looking for Open"
        },
        {
          "click": "open.png",
          "wait_after": 1.0,
          "toast": "Opened",
          "else": "Open was not on the screen"
        },
        {
          "click": "save.png",
          "navigate": "window-title.png",
          "toast": "Saved",
          "else": "Save was not on the screen"
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
- Corner **toast notifications** report success and failure even while the
  launcher is minimized. Click a toast to dismiss it early. Toasts do not
  steal keyboard or mouse focus from the target application.
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
6. Leaves the mouse still when `action` is `"find"`.
7. Moves the cursor to the match center for `"move"`, `"click"`, and
   `"double_click"`.
8. Clicks when `action` is `"click"` or `"double_click"` and `dry_run` is
   `false`.
9. Shows the step `toast` when one is set.
10. Waits for `wait_after`.
11. Continues to the next step.

If step 4 finds nothing and the step has `navigate`, the program moves to that
handle image and repeats steps 3-7 once for the original template.

Utility steps run their keyboard, wait, scroll, or toast action directly. Their
optional `delay` runs first and `wait_after` runs afterward.

If a step fails, the workflow stops immediately. A red toast explains what
failed: your `else` text when provided, plus the technical reason. Common
causes include:

- Image file missing or unreadable.
- Image not visible in the selected search area.
- Confidence set too high.
- Template larger than the search area.
- Invalid JSON or unsupported step property.
- Navigate handle also not found after an on-fail recovery.

Successful steps with `toast` show a green notification. Runtime failures no
longer open a blocking error dialog; the toast and status line are enough.

## Safety

PyAutoGUI's corner fail-safe is enabled. Move the cursor forcefully into a
screen corner to abort runaway mouse automation. The GUI reports that the
fail-safe was triggered.

Test a new workflow with `"dry_run": true` before allowing it to click.
Restricting a step with `region` or `distance` can also reduce accidental
matches.

## Currently unsupported workflow actions

Workflow steps currently support image-based mouse actions, waiting, typing,
writing paths, key presses, hotkeys, scrolling, toast notifications, variables,
`for` loops, optional steps, and a single on-fail navigate retry. The JSON
runner does not yet provide dedicated properties for:

- Dragging.
- Conditional branches beyond `else` messages, `try`, `needed`/`optional`,
  `skip_failed`, and `navigate` on fail.
- Repeated automatic retries (navigate retries once).
- Starting external programs.
- Creating files on disk (`write` only types the path).

Those features would require additions to the workflow validator and runner in
`main.py`.
