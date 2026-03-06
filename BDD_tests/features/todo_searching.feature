Feature: Search and Filter Todos
  As a user, I want to filter my tasks and check for routing consistency.

  Background:
    Given the system is cleared
    And a todo exists with title "Shopping" and doneStatus "true"
    And a todo exists with title "Work" and doneStatus "false"

  # NORMAL FLOW
  Scenario Outline: Filter todos by completion status
    When I GET "/todos?doneStatus=<status>"
    Then the response status should be "200"
    And all items in the response should have doneStatus <status>

    Examples:
      | status |
      | true   |
      | false  |

  # ALTERNATE FLOW
  Scenario Outline: Search by title keywords
    When I GET "/todos?title=<query>"
    Then the response status should be "200"
    And the number of items returned should be <count>

    Examples:
      | query      | count |
      | Shopping   | 1     |
      | Missing    | 0     |

  # ERROR FLOW (Technical/Routing Error: Greedy Routing)
  Scenario Outline: Verify routing for invalid sub-paths
    When I send an OPTIONS request to "<path>"
    Then the response status should be "<status>"

    Examples:
      | path                 | status | notes                          |
      | /todos/invalid_path  | 200    | Greedy Routing Bug (Collection) |
      | /todos/1/undefined   | 404    | Standard 404 (Instance)         |