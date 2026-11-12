# Contributing

## Publishing a Nightly Release

Maintainers can publish a nightly release from the GitHub **Releases** page:

1. Push the commit you want to package to GitHub.
2. Select **Draft a new release** and create a new tag for that commit using `v2.0.0-nightly-YYYYMMDD` (for example, `v2.0.0-nightly-20261112`).
3. Give the release a title, mark it as a **pre-release**, and publish it.

Publishing the release automatically starts the **Package Nightly Release** GitHub Actions workflow. The workflow packages the source at the release tag into `openPypelineStudio.zip` and attaches it to the release. The ZIP extracts into an `openPypelineStudio` folder. This action packages and uploads the ZIP; it does not create or publish the GitHub release itself.

To package an already-published nightly release, open **Actions** in GitHub, select **Package Nightly Release**, choose **Run workflow**, and enter the release tag.
