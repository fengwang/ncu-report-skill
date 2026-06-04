# Specification: Throughput Constants

## ADDED Requirements

### Requirement: RTX 5090 Peak Constants

`helpers/analyze_reports.py` SHALL define module-level constants for RTX 5090 peak throughput values derived from PRD Section 4.

#### Scenario: Bandwidth constant present
WHEN `grep -c '1792\|1.792' helpers/analyze_reports.py` is run
THEN it MUST return >= 1

#### Scenario: Constants match PRD
WHEN the constants are compared to PRD Section 4.2 and 4.3
THEN the bandwidth value MUST be approximately 1792 GB/s and the FP32 peak MUST be approximately 104.8 TFLOPS

### Requirement: Constants Used in Output

The peak constants SHALL be referenced when printing key metric summaries, providing context for efficiency percentages.

#### Scenario: Bandwidth context in output
WHEN analyze_reports.py processes a report and prints key metrics
THEN the output MUST include the RTX 5090 peak bandwidth value for reference
