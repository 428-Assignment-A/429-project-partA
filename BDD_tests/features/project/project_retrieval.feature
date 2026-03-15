Feature: Retrieve a Specific Course Project by ID
    As a user, I want to retrieve a specific course project by ID so that I can view its details.

    Background:
        Given the todo manager service is running
        And the system is cleared

    # NORMAL FLOW
    Scenario Outline: Retrieve an existing project by ID
        Given a project exists with title "<title>" and description "<description>" and active "<active>"
        And I store the id of the created project
        When I GET "/projects/{stored_id}"
        Then the response status should be "200"
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
    Scenario Outline: Retrieve a project that has linked tasks
        Given a project exists with title "<title>"
        And a todo exists with title "<todo_title>"
        And the todo is linked to the project
        And I store the id of the created project
        And I store the id of the created todo
        When I GET "/projects/{stored_project_id}"
        Then the response status should be "200"
        And the response tasks list should contain the stored todo id

        Examples:
            | title    | todo_title      |
            | ECSE 429 | Complete Part B |
            | FACC 300 | Read Slides     |

    # ERROR FLOW
    Scenario Outline: Fail to get a project with a non-existent ID
        When I GET "/projects/<id>"
        Then the response status should be "404"

        Examples:
            | id     |
            | 999999 |
            | 0      |