Feature: Unlink Todos from Projects
  As a user, I want to remove a todo from a project so that I can keep my project task list accurate.

  Background:
    Given the todo manager service is running
    And the system is cleared
    And a project exists with title "COMP 302" and description "Functional Programming" and active "true"
    And I store the id of the created project
    And a todo is created with title "A2 Submission"
    And I capture its dynamic ID
    And the todo is linked to the project

  # NORMAL FLOW
  Scenario: Unlink a todo from a project
    When I DELETE "/projects/{stored_project_id}/tasks/{stored_todo_id}"
    Then the response status should be "200"
    And a GET request to "/projects/{stored_project_id}/tasks" should not contain the todo

  # ALTERNATE FLOW
  Scenario: Unlinking a todo from a project does not delete the todo
    When I DELETE "/projects/{stored_project_id}/tasks/{stored_todo_id}"
    Then the response status should be "200"
    And a GET request to "/todos/{stored_todo_id}" should return "200"

  # ERROR FLOW
  Scenario Outline: Attempt to unlink a todo from a project using an invalid ID
    When I DELETE "/projects/<project_id>/tasks/<todo_id>"
    Then the response status should be "404"
    And the response body should contain an error message
    Examples:
      | project_id | todo_id |
      | 999999     | 1       |
      | 1          | 999999  |
