Feature: Delete a Course Project
    As a user, I want to delete a course project so that I can remove projects I no longer need.

    Background:
        Given the todo manager service is running
        And the system is cleared

    # NORMAL FLOW
    Scenario Outline: Delete an existing project by ID
        Given a project exists with title "<title>" and description "<description>" and active "<active>"
        And I store the id of the created project
        When I DELETE "/projects/{stored_id}"
        Then the response status should be "200"
        And a GET request to "/projects/{stored_id}" should return "404"

        Examples:
            | title    | description          | active |
            | ECSE 429 | Software Validation  | true   |
            | MATH 240 | Discrete Mathematics | true   |

    # ALTERNATE FLOW
    Scenario Outline: Delete a project that has a linked task
        Given a project exists with title "<title>"
        And a todo exists with title "<todo_title>"
        And the todo is linked to the project
        And I store the id of the created project
        And I store the id of the created todo
        When I DELETE "/projects/{stored_project_id}"
        Then the response status should be "200"
        And a GET request to "/projects/{stored_project_id}" should return "404"
        And a GET request to "/todos/{stored_todo_id}" should return "200"

        Examples:
            | title    | todo_title            |
            | ECSE 429 | Midterm Exam Revision |
            | COMP 303 | Submit A1             |

    # ERROR FLOW
    Scenario Outline: Fail to delete a project with a non-existent ID
        When I DELETE "/projects/{id}"
        Then the response status should be "404"

        Examples:
            | id     |
            | 999999 |
            | 0      |