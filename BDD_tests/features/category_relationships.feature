Feature: Manage Category Relationships
  As a user, I want to link categories to todos and projects so that I can organize my work under meaningful themes.

  Background:
    Given a category is created with title "Linked Category" and its ID is captured
    And a todo is created with title "Related Todo" and its ID is captured
    And a project is created with title "Related Project" and its ID is captured

  # NORMAL FLOW
  Scenario Outline: Link a category to a todo and verify the relationship
    When I POST to "/categories/<category_ref>/todos" with the captured todo ID
    Then the response status should be "201"
    And a GET to "/categories/<category_ref>/todos" should include the captured todo ID

    Examples:
      | category_ref  |
      | CAPTURED_ID   |

  # ALTERNATE FLOW
  Scenario Outline: Link a category to a project and verify the relationship
    When I POST to "/categories/<category_ref>/projects" with the captured project ID
    Then the response status should be "201"
    And a GET to "/categories/<category_ref>/projects" should include the captured project ID

    Examples:
      | category_ref  |
      | CAPTURED_ID   |

  # ERROR FLOW
  Scenario Outline: Attempt to link a category to a non-existent todo or project
    When I POST to "/categories/CAPTURED_ID/<endpoint>" with id "<invalid_id>"
    Then the response status should be "404"
    And the response body should contain an error message

    Examples:
      | endpoint | invalid_id |
      | todos    | 99999      |
      | projects | 99999      |
