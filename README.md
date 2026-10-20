# build.yaml

```yaml
name: Advanced Camera
commit: cdcef3fb69267178f3f224b12f5f6b862a205f6e
ai: H
path: .
arches: all
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
- `path` - the one spec or yaml sfosbuild builds, such as `rpm/app.spec`. Required. A repository can contain several specs; this names the entrypoint for this package.
- `overlay` - directory next to the recipe file whose files are copied onto the clone. Defaults to `overlay`. `go1_18/overlay` is that subdirectory.
- `patches` - directory next to the recipe file whose `*.patch` files are applied first. Defaults to `patches`.
- `arches` - Which architectures to build: `aarch64`, `armv7hl`, `i486`, or a comma-separated list of those. `all`, empty, or omitted builds all three.
- `description` - Description that appears in the UI
- `screenshots` - Screanshots that appear in the UI
- `install` - which packages should be installed by default, since one source can build multiple .rpms
- `repos` - extra https repositories installed into the build image. `{version}` is the Sailfish OS version (`5.1.0.11`), `{release}` is major.minor (`5.1`), and `{arch}` is `aarch64`, `armv7hl`, or `i486`. `{version}/{arch}` keeps the full version (`https://repo-oss.ftuna.eu/{version}/{arch}/`). `{version}_{arch}` follows Chum and uses major.minor from 4.6 (`https://repo.sailfishos.org/obs/sailfishos:/chum/{version}_{arch}/` becomes `5.1_aarch64`).

One upstream repository can contain several packages. `build.yaml` is one package. Another file in the same directory, such as `libfoo.yaml`, is another package from the same clone. Each has its own `path`, `overlay`, `patches`, `install`, and `repos`. The recipe id of `libfoo.yaml` is `github.com/owner/repo/libfoo`.

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