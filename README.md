# ECSE-429 Part A - Test Framework

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API (in separate terminal)
java -jar runTodoManagerRestAPI-1.5.5.jar

# Run tests
pytest -v
```

## Project Structure

```
tests/
├── todos/              # Deniz
├── projects/           # Karine
├── categories/         # Janelle
└── interoperability/   # Alisha
```

## Writing Tests

Copy `tests/todos/test_example.py` as a template.

Example:
```python
def test_something(self, api):
    response = api.get("/endpoint")
    assert response.status_code == 200
```

## Running Tests

```bash
pytest -v                           # Run all tests
pytest tests/todos/ -v              # Run todos tests only
pytest tests/todos/test_file.py -v  # Run specific file
```