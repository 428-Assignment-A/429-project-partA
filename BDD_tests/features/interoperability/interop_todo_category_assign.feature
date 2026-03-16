Feature: Assign Categories to Projects
  As a user, I want to assign a category to a project so that I can classify my course projects by type or theme.

  Background:
    Given the todo manager service is running
    And the system is cleared
    And a project exists with title "MATH 240" and description "Discrete Mathematics" and active "true"
    And I store the id of the created project
    And a category is created with title "Assignment" and its ID is captured

  # NORMAL FLOW
  Scenario: Assign a category to a project
    Given the category is linked to the project
    When I GET "/projects/{stored_project_id}/categories"
    Then the response status should be "200"
    And a GET request to "/projects/{stored_project_id}/categories" should return the linked category

  # ALTERNATE FLOW
  Scenario: Retrieve all categories linked to a project
    Given the category is linked to the project
    When I GET "/projects/{stored_project_id}/categories"
    Then the response status should be "200"
    And the response should contain the category title "Assignment"

  # ERROR FLOW
  Scenario Outline: Attempt to assign a category to a non-existent project
    When I POST to "/projects/<invalid_project_id>/categories" with category ID stored_category_id
    Then the response status should be "404"
    And the response body should contain an error message
    Examples:
      | invalid_project_id |
      | 999999             |
      | 0                  |
