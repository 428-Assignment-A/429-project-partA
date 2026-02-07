Based on the specifications, here's what each individual unit test module should contain:

## 📋 **Individual Unit Test Module Requirements**

### **Module Structure (Required Elements)**

Each test module must:

1. **System Readiness Check**
   - Verify API is running before tests execute
   - Fail fast if service unavailable

2. **State Management**
   - Save system state before tests
   - Restore system state after tests
   - Ensure tests can run in any order

3. **Test Setup**
   - Set up initial conditions for each test
   - Create necessary test data

4. **Test Execution & Assertions**
   - Execute the API operation
   - Assess correctness of results

---

### **Required Test Types (per module)**

Each module must include tests for:

#### **1. Core Functionality Tests**
- ✅ Confirm API does what it's supposed to do
- ✅ Test with typical/expected data
- ✅ Verify correct response structure
- ✅ Verify correct data returned

#### **2. Format Tests**
- ✅ Test with JSON payload (Content-Type: application/json)
- ✅ Verify XML response can be generated

#### **3. Return Code Tests**
- ✅ Verify correct status codes (200, 201, 404, 400, 405, etc.)
- ✅ Test expected success codes
- ✅ Test expected error codes

#### **4. Side Effects Tests**
- ✅ Verify operation only changes what it should
- ✅ Verify no unexpected data modifications
- ✅ Confirm other entities remain unchanged

#### **5. Command Line Query Tests**
- ✅ Verify endpoint works correctly via HTTP requests
- ✅ Test query parameters (if applicable)
- ✅ Test filtering (if applicable)

#### **6. When jar file is not running**
- ✅ Verify test fails when jar file is not running (localhost endpoint is not exposed)

---

### **Additional Tests (Based on Endpoint Type)**

#### **For Documented APIs:**
- ✅ Test matches documented behavior
- ✅ Test documented parameters
- ✅ Test documented response format

#### **For Undocumented APIs:**
- ✅ Document actual behavior found
- ✅ Test discovered functionality

#### **For Bugs (when behavior ≠ documentation):**
Create **TWO separate modules**:

**Module 1: Expected Behavior (FAILING)**
- ✅ Test what documentation says should happen
- ✅ Mark as expected failure
- ✅ This test will FAIL (because of bug)

**Module 2: Actual Behavior (PASSING)**
- ✅ Test what actually happens
- ✅ This test will PASS
- ✅ Documents the bug's actual behavior

---

## 📝 **Example Module Template**

```python
"""
test_get_todos.py - Tests for GET /todos endpoint

Tests:
1. Core functionality
2. JSON/XML payloads
3. Return codes
4. Side effects
5. Command line queries
"""

import pytest

class TestGetTodos:
    
    # 1. SYSTEM READINESS (handled by conftest fixture)
    
    # 2. CORE FUNCTIONALITY
    def test_get_todos_returns_all_todos(self, api):
        """Verify GET /todos returns all todo items"""
        response = api.get("/todos")
        assert response.status_code == 200
        assert "todos" in response.json()
    
    # 3. JSON FORMAT
    def test_get_todos_json_payload(self, api):
        """Verify JSON response format"""
        response = api.get("/todos", headers={"Accept": "application/json"})
        assert response.status_code == 200
        assert "application/json" in response.headers["Content-Type"]
    
    # 4. XML FORMAT
    def test_get_todos_xml_payload(self, api):
        """Verify XML response format"""
        response = api.get("/todos", headers={"Accept": "application/xml"})
        assert response.status_code == 200
        assert "xml" in response.headers["Content-Type"].lower()
    
    # 5. RETURN CODES
    def test_get_todos_returns_200(self, api):
        """Verify correct status code"""
        response = api.get("/todos")
        assert response.status_code == 200
    
    # 6. SIDE EFFECTS
    def test_get_todos_no_side_effects(self, api):
        """Verify GET doesn't modify data"""
        # Get initial state
        initial = api.get("/todos").json()
        
        # Perform GET
        api.get("/todos")
        
        # Verify state unchanged
        after = api.get("/todos").json()
        assert initial == after
    
    # 7. COMMAND LINE / QUERY PARAMETERS
    def test_get_todos_with_filter(self, api):
        """Verify query parameter filtering works"""
        response = api.get("/todos?doneStatus=true")
        assert response.status_code == 200
```

---

## 🎯 **Summary Checklist**

For each API endpoint, your module must test:

- [ ] **Functionality** - Does it work as specified?
- [ ] **JSON** - Accepts/returns JSON?
- [ ] **XML** - Accepts/returns XML?
- [ ] **Status Codes** - Returns correct codes?
- [ ] **Side Effects** - Only changes what it should?
- [ ] **State Management** - Saves/restores state?
- [ ] **Independence** - Runs in any order?

**Plus for bugs:**
- [ ] **Expected behavior** - Failing test showing what should happen
- [ ] **Actual behavior** - Passing test showing what does happen

---

## 📊 **Typical Module Size**

A complete unit test module typically has:
- **5-10 tests minimum** per endpoint
- More for complex endpoints with multiple parameters
- Separate modules for bugs (expected vs actual)