# Changelog

 All notable changes to this project will be documented in this file.

 The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
 and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

 The intended audience of this file is for `incydr` SDK and CLI consumers -- as such, changes that don't affect
 how a consumer would use the library or CLI tool (e.g. adding unit tests, updating documentation, etc) are not captured
 here.

## 1.0.1 2023-04-21

### Fixed

- Bug in the `user_risk_profile` client, where `get_page()` was using the incorrect query param for the page number.
