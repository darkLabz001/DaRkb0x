# Ragnar In DaRkb0x

This directory vendors `PierreGode/Ragnar` so DaRkb0x can ship a close
1:1 copy of the upstream project.

- Upstream: `https://github.com/PierreGode/Ragnar`
- Imported as a vendored tree, excluding only the upstream `.git/` directory
- DaRkb0x-specific integration lives in `darkbox_headless.py`

The vendored Ragnar app is launched from DaRkb0x through the payload
`payloads/utilities/ragnar.py`, which starts Ragnar's headless web stack on
port `8091` by default so it can coexist with DaRkb0x's own WebUI.
