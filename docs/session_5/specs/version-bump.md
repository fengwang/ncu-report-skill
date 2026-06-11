# Spec: NC-1 — Version Bump (CUDA 13.2 → 13.3)

## ADDED Requirements

### Requirement: ENVIRONMENT.md in blast radius
ENVIRONMENT.md SHALL be included in the session's allowed_files list.

#### Scenario: ENVIRONMENT.md version bump
WHEN ENVIRONMENT.md is read
THEN "CUDA 13.2" SHALL be replaced with "CUDA 13.3"

## MODIFIED Requirements

### Requirement: CUDA version references updated
All references to CUDA 13.2 outside docs/ SHALL be replaced with CUDA 13.3.

#### Scenario: Programming guide version
WHEN blackwell-cuda-programming.md is read
THEN the CUDA Toolkit version line SHALL read "13.3"

#### Scenario: README version
WHEN README.md is read
THEN the tested-with version SHALL read "13.3"

#### Scenario: Python API paths
WHEN reference/04-python-api.md is read
THEN all path references SHALL use "cuda-13.3" instead of "cuda-13.2"

#### Scenario: Common issues paths
WHEN reference/09-common-issues.md is read
THEN all path references SHALL use "cuda-13.3" instead of "cuda-13.2"

#### Scenario: Zero 13.2 references outside docs
WHEN `grep -rci 'CUDA 13\.2' --include='*.md' --include='*.py' --include='*.cu' --include='*.h' --exclude-dir=docs .` is run
THEN the output SHALL contain only lines ending in `:0`
