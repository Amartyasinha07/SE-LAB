# Lab 6: Code and Branch Coverage Analysis — Pet Boarding

Module under test: `pet_boarding.py`

## About

A Python module that calculates pet boarding fees, evaluates admission eligibility based on age and vaccinations, and determines checkout status based on remaining time and stay type.

## Deliverables & Files

| File | Description | Coverage Target |
|------|-------------|-----------------|
| `pet_boarding.py` | Application module under test | - |
| `CodeCoverageTest_49_pet_boarding.py` | Test suite focused on statement/line coverage | >90% Line Coverage (Achieved 95%) |
| `BranchCoverageTest_49_pet_boarding.py` | Test suite covering all decision branches and edge conditions | 100% Branch Coverage (Achieved 100%) |
| `test_pet_boarding.py` | Complete test suite for automated pytest test runners | 100% Full Coverage |
| `code_coverage_report.png` | Terminal report screenshot for Code Coverage analysis | - |
| `branch_coverage_report.png` | Terminal report screenshot for Branch Coverage analysis | - |

## How to Run

### 1. Code Coverage Analysis
```bash
coverage run -m pytest CodeCoverageTest_49_pet_boarding.py
coverage report -m
```

### 2. Branch Coverage Analysis
```bash
coverage run --branch -m pytest BranchCoverageTest_49_pet_boarding.py
coverage report -m
```

## Coverage Results Summary

### Milestone 1: Code Coverage
```
Name                                  Stmts   Miss  Cover   Missing
-------------------------------------------------------------------
CodeCoverageTest_49_pet_boarding.py      20      0   100%
pet_boarding.py                          37      2    95%   6, 8
-------------------------------------------------------------------
TOTAL                                    57      2    96%
```

### Milestone 2: Branch Coverage
```
Name                                    Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------------------
BranchCoverageTest_49_pet_boarding.py      57      0      0      0   100%
pet_boarding.py                            37      0     26      0   100%
-----------------------------------------------------------------------------------
TOTAL                                      94      0     26      0   100%
```
