Feature: Create Categories
  As a user, I want to create categories so that I can organize my todos and projects by topic or theme.

  Background:
    Given the todo manager service is running

  # NORMAL FLOW
  Scenario Outline: Create a category with valid title and optional description
    When I POST to "/categories" with title "<title>" and description "<description>"
    Then the response status should be "201"
    And the response body should contain title "<title>"
    And the new category ID should be stored for subsequent steps

    Examples:
      | title        | description                         |
      | Assignment   | Tasks for course assignments        |
      | Exam         | Upcoming exams and quizzes          |
      | Reading!@#   | Special character category title    |

  # ALTERNATE FLOW
  Scenario Outline: Create a category using different content types
    When I POST to "/categories" in "<format>" with title "<title>"
    Then the response status should be "201"
    And the "Content-Type" header should contain "<format>"

    Examples:
      | format           | title               |
      | application/json | Assignment Category |
      | application/xml  | Exam Category       |

  # ERROR FLOW
  Scenario Outline: Attempt to create a category with a missing or empty title
    When I POST to "/categories" with title "<title>"
    Then the response status should be "400"
    And the response body should contain an error message

    Examples:
      | title |
      |       |
