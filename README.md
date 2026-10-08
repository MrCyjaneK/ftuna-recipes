# build.yaml

```yaml
name: Advanced Camera
commit: cdcef3fb69267178f3f224b12f5f6b862a205f6e
ai: H
description: |
  Advanced Camera is a community camera application for Sailfish devices.

  - Effects
  - Focus mode
icon: https://raw.githubusercontent.com/piggz/harbour-advanced-camera/cdcef3fb69267178f3f224b12f5f6b862a205f6e/harbour-advanced-camera.svg
screenshots:
  - https://raw.githubusercontent.com/piggz/harbour-advanced-camera/cdcef3fb69267178f3f224b12f5f6b862a205f6e/screenshots/screenshot1.png
install:
  - harbour-advanced-camera
```

- `name` - How it should appear in the UI
- `commit` - What commit should we pull for build - this also pulls all submodules
- `ai` - [AI usage level](#ai-usage) - following Chum guidelines
- `description` - Description that appears in the UI
- `screenshots` - Screanshots that appear in the UI
- `install` - which packages should be installed by default, since one source can build multiple .rpms

## AI usage

FTuna follows Chum's AI usage discose policy.

| Value | Description |
| --- | --- |
| H | Human written code, no AI use at all |
| A | No AI-written code, AI used in other parts of the development process |
| B | AI-assisted, all code human-reviewed and/or rewritten |
| C | Some parts AI-coded |
| V | Fully or almost fully vibe-coded |
| X | Packager does not want to disclose |