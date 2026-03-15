Feature: Create Projects
    As a user, I want to create a new course project.

    Background:
        Given the todo manager service is running
        And the system is cleared

    # NORMAL FLOW
    Scenario Outline: Create a project with all fields
        When I POST to "/projects" with title "<title>" and description "<description>" and active "<active>"
        Then the response status should be "201"
        And the response should contain project title "<title>"
        And the response should contain project description "<description>"
        And the response should contain project active status "<active>"
        And the response should contain project completed status "false"

        Examples:
            | title    | description          | active |
            | ECSE 429 | Software Validation  | true   |
            | MATH 240 | Discrete Mathematics | true   |
            | FACC 300 | Engineering Economy  | false  |

    # ALTERNATE FLOW
    Scenario Outline: Create a project with only a title
        When I POST to "/projects" with title "<title>"
        Then the response status should be "201"
        And the response should contain project title "<title>"

        Examples:
            | title    |
            | COMP 302 |
            | BIOL 112 |

    # ERROR FLOW
    Scenario Outline: Fail to create a project when a pre-set ID is provided
        When I POST to "/projects" with title "<title>" and field "id" set to "<id>"
        Then the response status should be "400"

        Examples:
            | title    | id  |
            | COMP 303 | 999 |