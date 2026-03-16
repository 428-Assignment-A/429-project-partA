Feature: Relationship Integrity Across Entities
  As a user, I want relationships between todos, projects, and categories to remain consistent when entities are deleted so that my data stays accurate.

  Background:
    Given the todo manager service is running
    And the system is cleared
    And a project exists with title "ECSE 429" and description "Software Validation" and active "true"
    And I store the id of the created project
    And a todo is created with title "Write Test Report"
    And I capture its dynamic ID
    And a category is created with title "Exam" and its ID is captured
    And the todo is linked to the project
    And the category is linked to the todo

  # NORMAL FLOW
  Scenario: Deleting a project does not delete its linked todos
    When I DELETE "/projects/{stored_project_id}"
    Then the response status should be "200"
    And a GET request to "/todos/{stored_todo_id}" should return "200"

  # ALTERNATE FLOW
  Scenario: Deleting a category does not delete its linked todos or projects
    When I DELETE the captured category ID
    Then the response status should be "200"
    And a GET request to "/todos/{stored_todo_id}" should return "200"
    And a GET request to "/projects/{stored_project_id}" should return "200"

  # ERROR FLOW
  Scenario Outline: GET relationship endpoint for non-existent parent returns 404
    When I GET "<path>"
    Then the response status should be "404"
    And the response body should contain an error message
    Examples:
      | path                          |
      | /projects/999999/tasks        |
      | /todos/999999/categories      |
      | /projects/999999/categories   |
