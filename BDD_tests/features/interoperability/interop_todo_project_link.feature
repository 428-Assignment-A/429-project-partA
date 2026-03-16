Feature: Link Todos to Projects
  As a user, I want to link todos to a project so that I can organize my tasks under the correct course.

  Background:
    Given the todo manager service is running
    And the system is cleared
    And a project exists with title "ECSE 429" and description "Software Validation" and active "true"
    And I store the id of the created project
    And a todo is created with title "Submit Lab Report"
    And I capture its dynamic ID

  # NORMAL FLOW
  Scenario Outline: Link a todo to a project
    When I POST to "/projects/{stored_project_id}/tasks" with todo ID "<todo_ref>"
    Then the response status should be "201"
    And a GET request to "/projects/{stored_project_id}/tasks" should return the linked todo
    Examples:
      | todo_ref       |
      | stored_todo_id |

  # ALTERNATE FLOW
  Scenario Outline: Retrieve all todos linked to a project
    Given the todo is linked to the project
    When I GET "/projects/{stored_project_id}/tasks"
    Then the response status should be "200"
    And the "Content-Type" header should contain "<format>"
    And the response should contain the linked todo title "Submit Lab Report"
    Examples:
      | format           |
      | application/json |
      | application/xml  |

  # ERROR FLOW
  Scenario Outline: Attempt to link a todo to a non-existent project
    When I POST to "/projects/<invalid_id>/tasks" with todo ID stored_todo_id
    Then the response status should be "404"
    And the response body should contain an error message
    Examples:
      | invalid_id |
      | 999999     |
      | 0          |
