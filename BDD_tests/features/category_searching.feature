Feature: Search and Filter Categories
  As a user, I want to search and filter categories so that I can quickly locate the ones relevant to my current context.

  Background:
    Given the system is cleared
    And a category exists with title "Health" and description "Wellness related tasks"
    And a category exists with title "Finance" and description "Budget and expenses"

  # NORMAL FLOW
  Scenario Outline: Filter categories by title
    When I GET "/categories?title=<query>"
    Then the response status should be "200"
    And the number of category items returned should be <count>

    Examples:
      | query    | count |
      | Health   | 1     |
      | Finance  | 1     |

  # ALTERNATE FLOW
  Scenario Outline: Retrieve all categories and confirm response format
    When I GET "/categories" with Accept header "<format>"
    Then the response status should be "200"
    And the "Content-Type" header should contain "<format>"
    And the response should contain at least 2 categories

    Examples:
      | format           |
      | application/json |
      | application/xml  |

  # ERROR FLOW
  Scenario Outline: Search with a filter that matches no categories
    When I GET "/categories?title=<query>"
    Then the response status should be "200"
    And the number of category items returned should be 0

    Examples:
      | query        |
      | Nonexistent  |
      | 12345        |
