# Release Process

## Preparation

- Wait for the [tremor-runtime](https://github.com/tremor-rs/tremor-runtime) release to finish.
- update `TREMOR_VSN` variable in `Makefile` to point to the current version.
- regenerate cli, stdlib and api documentation: `make clean mkdocs.yml`
- Create a PR with those changes.

## Release

- Update `main` with the merged Pr from above.
- Tag the repo:
  * `git tag -a -m"Release v<MAJOR>.<MINOR>.<BUGFIX>" v<MAJOR>.<MINOR>.<BUGFIX> <COMMIT>`
  * `git push origin --tag`
- Go to bed.