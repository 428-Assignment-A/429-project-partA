Feature: Delete Todo Tasks
  As a user, I want to remove tasks and verify the ID is no longer accessible.

  Background:
    Given a todo is created and its ID is captured

  # NORMAL FLOW
  Scenario: Delete an existing task
    When I DELETE the captured ID
    Then the response status should be "200"
    And a GET request to the captured ID should return "404"

  # ALTERNATE FLOW
  Scenario Outline: Verify safe methods do not delete the resource
    When I send a "<method>" request to the captured ID
    Then the response status should be "200"
    And the captured ID should still exist

    Examples:
      | method  |
      | HEAD    |
      | OPTIONS |

  # ERROR FLOW (User Error: Re-deleting or non-existent)
  Scenario Outline: Attempt to delete invalid or already deleted IDs
    When I DELETE the resource at "<path>"
    Then the response status should be "404"

    Examples:
      | path         |
      | /todos/0     |
      | /todos/-1    |
      | ALREADY_DEL  |