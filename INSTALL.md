# v7 Testing Infrastructure - Installation for Theo-van-Gogh

## Installation

### 1. Extract and Copy Files

```bash
cd your-theo-van-gogh-folder
tar -xzf v7-testing-theo.tar.gz

# Copy test configuration
cp v7-testing-theo/pytest.ini .
cp v7-testing-theo/requirements-dev.txt .

# Copy test files
cp -r v7-testing-theo/tests .

# Copy GitHub Actions
cp -r v7-testing-theo/.github .

# Copy documentation
cp v7-testing-theo/TESTING.md .
cp v7-testing-theo/CHANGELOG.md .
```

### 2. Install Dependencies

```bash
source venv/bin/activate
pip install -r requirements-dev.txt
```

### 3. Run Tests

```bash
pytest

# With coverage
pytest --cov=src --cov-report=html
```

## Project Structure

```
Theo-van-Gogh/
├── pytest.ini
├── requirements-dev.txt
├── TESTING.md
├── CHANGELOG.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_file_manager.py
│   ├── test_file_organizer.py
│   └── test_upload_tracker.py
└── src/
    └── ...
```

## GitHub Badge

Add to your README.md:
```markdown
![Tests](https://github.com/YOUR_USERNAME/Theo-van-Gogh/workflows/Theo-van-Gogh%20CI/badge.svg)
```

## What's Tested

✅ FileManager (9 tests)
✅ UploadTracker (11 tests)  
✅ FileOrganizer (6 tests)

**Total: 26 tests**

## Next Steps

1. Run tests: `pytest`
2. Check coverage: `pytest --cov=src --cov-report=html`
3. Push to GitHub
4. Watch tests run automatically in Actions tab
