# Releasing

To release a new version:

- Make changes on a branch
- Update CHANGELOG for next release
- Run `bump-my-version bump {major|minor|patch}`
- Open a PR and have it merged to `main` after review
- Tag latest commit on `main` with the version, and push. This will trigger a
  build of the `data-access-tool-api` and `data-access-tool-server` images with
  the given version tag.
- Deploy the latest change with
  [garrison](https://bitbucket.org/nsidc/garrison). See the
  [section on garrison](#garrison) below for more info.

## garrison

[garrison](https://bitbucket.org/nsidc/garrison) is a deployment system for
NSIDC applications deployed to a VM on NSIDC infrastructure.

The [jenkins-cd](http://ci.jenkins-cd.apps.int.nsidc.org:8080) Jenkins VM
provides a mechanism for doing garrison deployments of the
`data-access-tool-backend` to integration and QA.

The
[Deploy Project with Garrison](https://ci.jenkins-ops-2022.apps.int.nsidc.org/job/Deploy_Project_with_Garrison/)
job defined in the Ops Jenkins is used by Ops to deploy to staging and
production.

See the [data-access-tool-vm](https://github.com/nsidc/data-access-tool-vm)
project for additional details and VM configuration for the
`data-access-tool-backend`.
