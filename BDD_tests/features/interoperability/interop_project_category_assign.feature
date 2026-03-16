Feature: Assign Categories to Todos
  As a user, I want to assign a category to a todo so that I can group related tasks by topic or theme.

  Background:
    Given the todo manager service is running
    And the system is cleared
    And a todo is created with title "Review Lecture Notes"
    And I capture its dynamic ID
    And a category is created with title "Exam" and its ID is captured

  # NORMAL FLOW
  Scenario Outline: Assign a category to a todo
    When I POST to "/todos/{stored_todo_id}/categories" with category ID "<category_ref>"
    Then the response status should be "201"
    And a GET request to "/todos/{stored_todo_id}/categories" should return the linked category
    Examples:
      | category_ref       |
      | stored_category_id |

  # ALTERNATE FLOW
  Scenario: Retrieve categories of a todo after linking
    Given the category is linked to the todo
    When I GET "/todos/{stored_todo_id}/categories"
    Then the response status should be "200"
    And the response should contain the category title "Exam"

  # ERROR FLOW
  Scenario Outline: Attempt to assign a non-existent category to a todo
    When I POST to "/todos/{stored_todo_id}/categories" with category ID "<invalid_id>"
    Then the response status should be "404"
    And the response body should contain an error message
    Examples:
      | invalid_id |
      | 999999     |
      | 0          |
