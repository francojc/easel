---
description: "Initialize and verify development environment for Easel CLI milestone development"
allowed-tools: ["Bash", "Read"]
---

# Milestone Development Environment Setup

You are setting up the development environment for autonomous milestone development on the **Easel CLI** project.

## Prerequisites Verification

First, verify all required tools are installed:

!python --version
!poetry --version
!git --version
!gh --version

## Environment Initialization

Initialize the development environment:

!poetry install --with dev
!poetry shell
!pre-commit install

## Setup Verification

Verify the setup is working correctly:

!poetry run pytest --version
!poetry run black --version
!poetry run flake8 --version
!poetry run mypy --version

## Read Project Context

Review the main project specification and current milestone specifications:

@easel-spec.md
@specs/

## Environment Status Check

Confirm the environment is ready for milestone development:

!git status
!poetry show
!poetry run pre-commit run --all-files || echo "Pre-commit hooks may fail on first run - this is normal"

Your development environment is now configured for autonomous milestone development. You can proceed with `/milestone:analyze <milestone-number>` to begin milestone implementation.
