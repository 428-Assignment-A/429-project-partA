Feature: Update a Course Project
    As a user, I want to update a course project so that I can keep its information current.

    Background:
        Given the todo manager service is running
        And the system is cleared

    # NORMAL FLOW
    Scenario Outline: Update all fields of an existing project using PUT
        Given a project exists with title "ECSE 429" and description "Old Description" and active "false"
        And I store the id of the created project
        When I PUT "/projects/{stored_id}" with title "<title>" and description "<description>" and active "<active>" and completed "<completed>"
        Then the response status should be "200"
        And the response should contain project title "<title>"
        And the response should contain project description "<description>"
        And the response should contain project active status "<active>"
        And the response should contain project completed status "<completed>"

        Examples:
            | title    | description          | active | completed |
            | COMP 303 | Software Design      | true   | true      |
            | MATH 240 | Discrete Mathematics | true   | false     |
            | FACC 300 | Engineering Economy  | false  | false     |

    # ALTERNATE FLOW
    Scenario Outline: Update only the title of an existing project
        Given a project exists with title "ECSE 429" and description "Old Description" and active "false"
        And I store the id of the created project
        When I PUT "/projects/{stored_id}" with title "<title>"
        Then the response status should be "200"
        And the response should contain project title "<title>"

        Examples:
            | title    |
            | COMP 302 |
            | BIOL 112 |

    # ERROR FLOW
    Scenario Outline: Fail to update a project with a non-existent ID
        When I PUT "/projects/<id>" with title "COMP 000"
        Then the response status should be "404"

        Examples:
            | id     |
            | 999999 |
            | 0      |