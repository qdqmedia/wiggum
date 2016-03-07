Wiggum [![Wiggum docs](https://img.shields.io/badge/docs-wiggum-brightgreen.svg)](http://qdqmedia.github.io/wiggum/) [![Build Status](https://travis-ci.org/qdqmedia/wiggum.svg?branch=master)](https://travis-ci.org/qdqmedia/wiggum)
=======

## Description

A modern centralized authentication and authorization system based on JWT.

![Wiggum flow](docs/img/wiggum.png)

## What can Wiggum do?

At this moment Wiggum can do a little bit more than login and logout:

* Login
* Logout
* JWT based authentication
* User, apps & permission models and API
* Admin panel
* Login/logout endpoints
* Default theme (clancy)
* Password reset links (expiration included)
* SFA (Single factor authentication) login with a link
* Theme selector based on ID, theme name or appID
* Redirect param on important URIs like login or logout
* Dev and CI environment based on docker and docker compose
* Impersonation of users
* JWT versioning (used for invalidation)
* JWT transition keys (two valid jwt keys at a time)
* Prometheus metrics

## Why this project was created?

Wiggum started with the need of a centralized auth system for all [QDQMedia](http://qdqmedia.com/) applications in order
to let the client (and QDQMedia workers) do the login once and access to all of our products.

## Documentation

Check the [documentation](http://qdqmedia.github.io/wiggum/) for more information

## Changelog

See [changelog](CHANGELOG.md)

## License

See [license](LICENSE)

## Authors

See [authors](AUTHORS) & [contributors](CONTRIBUTORS)
