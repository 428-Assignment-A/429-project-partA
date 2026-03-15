Feature: Complete Todo Tasks
  As a user, I want to toggle task completion and request specific response formats.

  Background:
    Given a todo is created and its ID is captured

  # NORMAL FLOW
  Scenario Outline: Toggle completion status
    When I POST to the captured ID with doneStatus <status>
    Then the response status should be "200"
    And the todo should show doneStatus as <status>

    Examples:
      | status |
      | true   |
      | false  |

  # ALTERNATE FLOW
  Scenario Outline: Request resource details in different formats
    When I GET the captured ID with Accept header "<format>"
    Then the response status should be "200"
    And the "Content-Type" header should match "<format>"

    Examples:
      | format           |
      | application/json |
      | application/xml  |

  # ERROR FLOW (User Error: Bad logic values)
  Scenario Outline: Update task with invalid completion values
    When I POST to the captured ID with doneStatus "<bad_value>"
    Then the response status should be "400"

    Examples:
      | bad_value |
      | maybe     |
      | 1         |