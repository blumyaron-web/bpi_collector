# Report Data Module

This module contains data and utilities used by the ReportGenerator class.

## Purpose

The purpose of this module is to separate data and styling information from the business logic in the report_generator.py module. This separation of concerns makes the code more maintainable and easier to test.

## Module Structure

- `__init__.py`: Makes this directory a Python package
- `formatting.py`: Contains functions for formatting timestamps and calculating durations
- `images.py`: Contains functions for working with images, such as encoding them to base64
- `styles.py`: Contains functions for getting report styles and templates
- `templates.py`: Contains HTML template fragments used in report generation

## Usage

The report_generator.py module imports and uses the functions provided by this module. For example:

```python
from .report_data.styles import get_report_styles
from .report_data.formatting import format_timestamp
from .report_data.images import encode_image_base64
```

## Benefits

- **Separation of concerns**: Data and styling information is separated from business logic
- **Reusability**: Functions can be reused in other modules
- **Testability**: Functions can be tested independently
- **Maintainability**: Easier to update styling or templates without affecting business logic