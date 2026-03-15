Feature: Update Categories
  As a user, I want to update category details so that my categories stay accurate and relevant over time.

  Background:
    Given a category is created with title "Assignment"
    And I capture its dynamic category ID

  # NORMAL FLOW
  Scenario Outline: Update specific fields of a category using POST
    When I POST to the captured category ID with "<field>" as "<value>"
    Then the response status should be "200"
    And the category should have "<field>" set to "<value>"

    Examples:
      | field       | value                        |
      | title       | Exam                         |
      | description | Covers lectures 1 through 5  |

  # ALTERNATE FLOW
  Scenario Outline: Replace a category entirely using PUT
    When I PUT to the captured category ID with title "<title>" and description "<description>"
    Then the response status should be "200"
    And the category should match the title "<title>"

    Examples:
      | title    | description                     |
      | Reading  | Weekly reading assignments      |
      | Exam     | Midterm and final exam category |

  # ERROR FLOW
  Scenario Outline: Attempt to modify the immutable ID field of a category
    When I POST to the captured category ID with an ID field set to "<new_id>"
    Then the response status should be "400"
    And the error message should be "Failed Validation: id should be ID"

    Examples:
      | new_id |
      | 9999   |
      | abc    |
