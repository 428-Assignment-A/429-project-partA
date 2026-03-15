Feature: Update Todo Tasks
  As a user, I want to modify a task I just created using its dynamic ID.

  Background:
    Given a todo is created with title "Initial State"
    And I capture its dynamic ID

  # NORMAL FLOW
  Scenario Outline: Update specific fields using POST
    When I POST to the captured ID with "<field>" as "<value>"
    Then the response status should be "200"
    And the todo should have "<field>" set to "<value>"

    Examples:
      | field       | value          |
      | title       | New Title      |
      | description | Updated Desc   |

  # ALTERNATE FLOW
  Scenario Outline: Replace a todo entirely using PUT
    When I PUT to the captured ID with title "<title>" and doneStatus <status>
    Then the response status should be "200"
    And the todo should match the title "<title>"

    Examples:
      | title    | status |
      | Replace1 | true   |
      | Replace2 | false  |

  # ERROR FLOW (User Error: Trying to change the ID)
  Scenario Outline: Attempt to modify the immutable ID field
    When I POST to the captured ID with an ID field set to "<new_id>"
    Then the response status should be "400"
    And the error message should be "Failed Validation: id should be ID"

    Examples:
      | new_id |
      | 9999   |
      | abc    |