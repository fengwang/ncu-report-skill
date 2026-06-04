# Specification: Harness Compile Target

## MODIFIED Requirements

### Requirement: sm_120 Compile Target

All compilation commands and examples in `helpers/harness_template.cu` SHALL target sm_120.

#### Scenario: No sm_100 references
WHEN `grep -i 'sm_100\|compute_100' helpers/harness_template.cu` is run
THEN it MUST return zero matches

#### Scenario: sm_120 compile command present
WHEN the file header comment is read
THEN the compile example MUST contain `-gencode=arch=compute_120,code=sm_120` or equivalent

#### Scenario: Template compiles
WHEN `nvcc -arch=sm_120 -lineinfo helpers/harness_template.cu -o /tmp/test_harness` is run
THEN it MUST succeed (exit code 0) OR the template is acknowledged as a stub requiring user edits (with compile-ready instructions in comments)

### Requirement: README Compile Example

The compile example in `helpers/README.md` SHALL use sm_120.

#### Scenario: README compile command
WHEN the README.md compile example is read
THEN it MUST contain `sm_120` and MUST NOT contain `sm_100`
