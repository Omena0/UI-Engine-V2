# Tests

This directory contains the reorganized test suite for the UI Engine V2 project.

## Structure

```
tests/
├── conftest.py                 # Shared test configuration and fixtures
├── integration/                # Integration tests
│   └── test_workflow.py       # End-to-end workflow tests
└── unit/                      # Unit tests
    ├── components/            # Component-specific tests
    │   ├── base/             # Base component functionality
    │   ├── button/           # Button component tests
    │   ├── checkbox/         # CheckBox component tests
    │   ├── childwindow/      # ChildWindow component tests
    │   ├── dropdown/         # Dropdown component tests
    │   ├── field/            # Field component tests
    │   ├── frame/            # Frame component tests
    │   ├── iconbutton/       # IconButton component tests
    │   ├── image/            # Image component tests
    │   ├── label/            # Label component tests
    │   ├── progress/         # ProgressBar component tests
    │   ├── radio/            # Radio component tests
    │   ├── segmented/        # SegmentedButton component tests
    │   ├── slider/           # Slider component tests
    │   ├── tabframe/         # TabFrame component tests
    │   └── toggle/           # Toggle component tests
    └── core/                 # Core module tests
        ├── input/            # Input system tests
        ├── text/             # Text rendering tests
        ├── theme/            # Theme system tests
        ├── util/             # Utility function tests
        └── window/           # Window core tests
```

## Running Tests

### All Tests
```bash
pytest tests/
```

### Specific Component Tests
```bash
pytest tests/unit/components/button/
pytest tests/unit/components/label/
```

### Core Module Tests
```bash
pytest tests/unit/core/window/
pytest tests/unit/core/input/
```

### Integration Tests
```bash
pytest tests/integration/
```

## Test Organization

- **Components**: Each UI component has its own test directory with comprehensive tests
- **Core Modules**: Engine core functionality is tested separately
- **Integration**: End-to-end tests that verify component interactions
- **Shared Fixtures**: Common test utilities and fixtures in `conftest.py`

## Test Naming Conventions

- Test files: `test_<component_name>.py`
- Test classes: `Test<ComponentName>`
- Test methods: `test_<functionality>`

## Previous Test Files

The following old test files have been reorganized and can be removed:
- `test_components.py`
- `test_childwindow_coverage.py`
- `test_comprehensive_coverage.py` 
- `test_core_modules.py`
- `test_coverage_boost.py`
- `test_dropdown_coverage.py`
- `test_final_coverage.py`
- `test_image_coverage.py`
- `test_input_coverage.py`
- `test_input_focused.py`
- `test_input_manager.py`
- `test_missing_components.py`
- `test_targeted_coverage.py`
- `test_text_coverage.py`
- `test_window_coverage.py`
