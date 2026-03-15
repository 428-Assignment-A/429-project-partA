Feature: Delete Categories
  As a user, I want to delete categories I no longer need so that my workspace stays clean and uncluttered.

  Background:
    Given a category is created with title "Old Assignment" and its ID is captured

  # NORMAL FLOW
  Scenario: Delete an existing category
    When I DELETE the captured category ID
    Then the response status should be "200"
    And a GET request to the captured category ID should return "404"

  # ALTERNATE FLOW
  Scenario Outline: Verify safe methods do not delete the category
    When I send a "<method>" request to the captured category ID
    Then the response status should be "200"
    And the captured category ID should still exist

    Examples:
      | method  |
      | HEAD    |
      | GET     |

  # ERROR FLOW
  Scenario Outline: Attempt to delete invalid or already-deleted category IDs
    When I DELETE the category at "<path>"
    Then the response status should be "404"

    Examples:
      | path              |
      | /categories/0     |
      | /categories/-1    |
      | ALREADY_DELETED   |
