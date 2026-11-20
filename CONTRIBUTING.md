# Contributing

Thank you for contributing to **openPypeline Studio**!

## Repository Architecture & Boundaries

Keep code organized across three clear layers so shared functionality stays reusable without requiring any DCC SDK at import time:

* **`openpypeline/core/`**: Host-agnostic pipeline logic, data models, preferences, localization, and core add-ons. Never import `maya`, `hou`, `nuke`, or Qt widgets here.
* **`openpypeline/ui/`**: Shared, host-agnostic PySide6 views and controllers (`OpsMainUI`, `OpsMainController`, dialogs, and `DiagnosticUI`).
* **`openpypeline/app/<host>/`**: Lightweight DCC-specific integrations providing file-handler adapters, loaders, host-specific add-ons, and thin UI subclasses for native docking/parenting.

## Running Tests

Run the headless unit and protocol-contract test suite from the repository root (no DCC installation required):

```bash
python3 -m unittest discover -s tests -v
```

New host integrations under `openpypeline/app/<host>/` must satisfy the file-handler and loader protocols verified in `tests/test_host_adapters.py`.

## Building Documentation

To regenerate the Sphinx API pages and build the HTML documentation locally with warnings treated as errors:

```bash
rm -f docs/openpypeline*.rst && sphinx-apidoc -f -o docs/ openpypeline/ && sphinx-build -b html -W --keep-going docs/ docs/_build/html
```

## Publishing a Nightly Release

Maintainers can publish a nightly release from the GitHub **Releases** page:

1. Push the commit you want to package to GitHub.
2. Select **Draft a new release** and create a new tag for that commit using `v2.0.0-nightly-YYYYMMDD` (for example, `v2.0.0-nightly-20261112`).
3. Give the release a title, mark it as a **pre-release**, and publish it.

Publishing the release automatically starts the **Package Nightly Release** GitHub Actions workflow. The workflow packages the source at the release tag into `openPypelineStudio.zip` and attaches it to the release. The ZIP extracts into an `openPypelineStudio` folder. This action packages and uploads the ZIP; it does not create or publish the GitHub release itself.

To package an already-published nightly release, open **Actions** in GitHub, select **Package Nightly Release**, choose **Run workflow**, and enter the release tag.
