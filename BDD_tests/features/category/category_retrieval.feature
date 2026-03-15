Feature: Retrieve Categories
  As a user, I want to retrieve category details so that I can view task type information for my courses accurately.

  Background:
    Given a category is created with title "Assignment", description "Tasks for course assignments", and its ID is captured

  # NORMAL FLOW
  Scenario Outline: Retrieve a specific category by ID and verify its fields
    When I GET the captured category ID
    Then the response status should be "200"
    And the response should contain field "<field>" with value "<value>"

    Examples:
      | field       | value                        |
      | title       | Assignment                   |
      | description | Tasks for course assignments |

  # ALTERNATE FLOW
  Scenario Outline: HEAD request on categories endpoint returns 200 with no body
    When I HEAD "<url>"
    Then the response status should be "200"
    And the response body should be empty

    Examples:
      | url         |
      | /categories |

  Scenario: HEAD request on a specific category returns 200 with no body
    When I HEAD the captured category ID
    Then the response status should be "200"
    And the response body should be empty

  # ERROR FLOW
  Scenario Outline: GET a non-existent category ID returns 404
    When I GET "/categories/<id>"
    Then the response status should be "404"
    And the response body should contain an error message

    Examples:
      | id    |
      | 99999 |
      | 0     |
