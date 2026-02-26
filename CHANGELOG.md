# Changelog

All notable changes to easel are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.1.2] - 2026-02-25

### Added

- XDG-compliant global config: respects `$XDG_CONFIG_HOME`
  (default `~/.config/easel/config.toml`)
- `--defaults` flag on `easel config global` for non-interactive setup
- `--local` flag on `easel commands install` to install skill commands
  into the current repo's `.claude/commands/` instead of globally
- `easel commands install` now covers all 6 command groups (assess,
  assignments, content, course, discuss, grading)

### Changed

- Local config moved from `.claude/course_parameters.yaml` (YAML)
  to `./easel/config.toml` (TOML)
- Improved `--help` text across all sub-apps and commands
- README rewritten as a user-facing document with standard structure

### Removed

- `pyyaml` dependency (all config is now TOML)

## [0.1.1] - 2026-02-25

### Added

- `--anonymize` flag for FERPA-compliant PII stripping on
  `assess setup`, `grading submissions`, and `grading show`
- `anonymize` field in local course config
- Claude Code skill commands for assignments, content, course,
  discuss, and grading groups

### Changed

- `assess:setup` and `course:setup` skill commands read `anonymize`
  from course config

### Fixed

- Removed deprecated `.direnv/bin/nix-direnv-reload` script

## [0.1.0] - 2026-02-23

Initial release. Full Canvas LMS CLI for instructor workflows.

### Added

- **Core layer:** `CanvasClient` (httpx async, pagination, 429 retry),
  `Config` (pydantic-settings), `CourseCache` (bidirectional code/ID
  mapping)
- **Courses:** `list`, `show`, `enrollments`
- **Assignments:** `list`, `show`, `create`, `update`, `rubrics`,
  `rubric`
- **Grading:** `submissions`, `show`, `submit`, `submit-rubric`
- **Assessment workflow:** `setup`, `load`, `update`, `submit`
  (dry-run by default, `--confirm` to post)
- **Modules:** `list`, `show`, `create`, `update`, `delete`
- **Pages:** `list`, `show`, `create`, `update`, `delete`
  (slug-based identification)
- **Discussions:** `list`, `show`, `create`, `update`
  (with announcement support)
- **Config sub-app:** `init`, `global`, `show` with YAML/TOML
  file management and global-to-local inheritance
- **Commands sub-app:** `install` to copy assess skill commands
  to `~/.claude/commands/`
- Three output formats: `table`, `json`, `plain`
- Shell completion via `--install-completion`
- `--test` flag for Canvas API connectivity check
- 234 tests passing across services and CLI layers

[0.1.2]: https://github.com/francojc/easel/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/francojc/easel/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/francojc/easel/releases/tag/v0.1.0
