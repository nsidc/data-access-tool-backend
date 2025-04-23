# Releasing

To release a new version:

- Make changes on a branch
- Update CHANGELOG for next release
- Run `bump-my-version bump {major|minor|patch}`
- Open a PR and have it merged to `main` after review
- Tag latest commit on `main` with the version, and push. This will trigger a
  build of the `data-access-tool-api` and `data-access-tool-server` images with
  the given version tag.
- Deploy the latest change with the
  [data-access-tool-vm](https://github.com/nsidc/data-access-tool-vm).
