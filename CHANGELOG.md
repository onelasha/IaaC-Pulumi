# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `.env` file support with `python-dotenv` for managing environment variables
- `.env.example` template with all common configuration variables
- "Bootstrap Infrastructure" section documenting manual one-time setup
- "Adding New Environments" section with step-by-step guide
- "Glossary" section with definitions of key terms
- Environment CIDR range table for avoiding network conflicts

### Changed
- Updated Quick Start guide to emphasize "preview before apply" best practice
- Improved `pulumi stack init` documentation to handle existing stacks
- Renumbered Quick Start steps to include environment configuration

### Fixed
- Fixed `AppInsightsComponent` duplicate `resource_name` argument error

## [0.1.0] - 2025-01-22

### Added
- Initial project structure with modular architecture
- Core infrastructure module (resource groups, naming, tags)
- Networking module (VNet, NSG, subnets)
- Security module (Key Vault, Managed Identity)
- Storage module (Storage Account, blob containers)
- Monitoring module (Log Analytics, App Insights)
- Environment-specific settings (dev, staging, prod)
- CrossGuard security policies
- Unit tests for naming and tagging
- Deployment and validation scripts
- Azure Blob Storage backend for Pulumi state
- Comprehensive README documentation

---

## How to Update This Changelog

When making changes to the project:

1. Add entries under `[Unreleased]` section
2. Use these categories:
   - **Added** - New features
   - **Changed** - Changes to existing functionality
   - **Deprecated** - Features to be removed in future
   - **Removed** - Features removed in this release
   - **Fixed** - Bug fixes
   - **Security** - Vulnerability fixes

3. When releasing, move `[Unreleased]` items to a new version section:
   ```markdown
   ## [0.2.0] - YYYY-MM-DD
   ```

4. Keep entries concise but descriptive
5. Link to issues/PRs where relevant: `([#123](link))`
