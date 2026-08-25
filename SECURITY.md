# Security policy

## Supported versions

Until `1.0.0`, security fixes go to the latest published `0.x` release.

| Version | Supported |
| --- | --- |
| 0.1.x | Yes, once published to PyPI |
| < 0.1 | No |

## Reporting a vulnerability

**Do not open a public GitHub issue for a security report.**

Use [GitHub private vulnerability reporting](https://github.com/SVamseekar/moveq/security/advisories/new).

If that form is unavailable, email **martisoura@gmail.com** with:

- a description of the issue
- the affected package and version (`moveq`, `moveq-core`, `moveq-catalogue`, or `moveq-cli`)
- steps to reproduce
- any suggested fix

You should receive an acknowledgement within 7 days. Please give us a reasonable window to publish a fix before any public disclosure.

## What this project does not handle

`moveq` is a local computation library. It does not run a network service, store credentials, or process authentication. Typical reports that belong here are:

- path or file handling bugs in the CLI that could read unintended files
- packaging artifacts that ship secrets or unintended files
- supply-chain issues in the GitHub Actions publish workflow

## Release credentials

Production publishes use [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC). There is no long-lived PyPI API token in this repository or on maintainer machines for production releases. See [docs/publishing.md](docs/publishing.md).
