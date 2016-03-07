# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).



## [0.1.0] - 2016-03-05
### Added
- Initial release
- Login
- Logout
- JWT based authentication
- User, apps & permission models and API
- Admin panel
- Login/logout endpoints
- Default theme (clancy)
- Password reset links (expiration included)
- SFA (Single factor authentication) login with a link
- Theme selector based on ID, theme name or appID
- Redirect param on important URIs like login or logout
- Dev and CI environment based on docker and docker compose
- Impersonation of users
- JWT versioning (used for invalidation)
- JWT transition keys (two valid jwt keys at a time)
- Prometheus metrics
- documentation
