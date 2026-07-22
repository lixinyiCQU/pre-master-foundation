# Refactoring Architecture

## Current problem
The single script mixes file access, validation, analysis, reporting, and CLI behavior.

## Module responsibilities
- data_loader.py: CSV I/O and record validation
- analyzer.py: statistics over valid records
- report.py: render and write analysis results
- main.py: CLI, logging configuration, orchestration, exit codes

## Dependency direction
main -> data_loader -> analyzer -> report

## Behavior that must remain stable
- Best experiment selection rule
- Average accuracy calculation
- Invalid-row handling
- Required CSV fields

## project architecture
exercises/python/log_analyzer/
├── README.md
├── data/
│   └── experiments.csv
├── output/
│   └── .gitkeep
├── notes/
│   ├── baseline_output.txt
│   ├── architecture.md
│   └── refactor_comparison.md
└── log_analyzer/
    ├── __init__.py
    ├── data_loader.py
    ├── analyzer.py
    ├── report.py
    └── main.py
