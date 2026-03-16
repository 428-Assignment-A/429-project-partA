Feature: Create Todo Tasks
  As a user, I want to create new todo tasks and verify they receive unique identifiers.

  Background:
    Given the todo manager service is running

  # NORMAL FLOW
  Scenario Outline: Create a todo with various valid titles
    When I POST to "/todos" with title "<title>" and description "<description>"
    Then the response status should be "201"
    And the response body should contain title "<title>"
    And the new ID should be stored for subsequent steps

    Examples:
      | title          | description        |
      | Submit Lab     | Finish part 5B     |
      | Special-!@#    | Special characters |

  # ALTERNATE FLOW
  Scenario Outline: Create a todo using different content types
    When I POST to "/todos" in "<format>" with title "<title>"
    Then the response status should be "201"
    And the "Content-Type" header should contain "<format>"

    Examples:
      | format           | title      |
      | application/json | JSON Task  |
      | application/xml  | XML Task   |

  # ERROR FLOW (User Error: Invalid Data Types)
  @xfail
  Scenario Outline: Create a todo with invalid data types
    When I POST to "/todos" with a <type> value of <value>
    Then the response status should be "400"

    Examples:
      | type       | value  |
      | title      | true   |
      | title      | 12345  |