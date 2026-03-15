Feature: List All Course Projects
    As a user, I want to retrieve all course projects so that I can see all existing projects.

    Background:
        Given the todo manager service is running
        And the system is cleared

    # NORMAL FLOW
    Scenario: List all projects when multiple projects exist
        Given a project exists with title "ECSE 429" and description "Software Validation" and active "true"
        And a project exists with title "MATH 240" and description "Discrete Mathematics" and active "true"
        When I GET "/projects"
        Then the response status should be "200"
        And the response should contain project title "ECSE 429"
        And the response should contain project title "MATH 240"

    # ALTERNATE FLOW
    Scenario: Filter projects by title
        Given a project exists with title "ECSE 429" and description "Software Validation" and active "true"
        And a project exists with title "MATH 240" and description "Discrete Mathematics" and active "true"
        And a project exists with title "MATH 240" and description "Advanced Math" and active "true"
        When I GET "/projects?title=MATH%20240"
        Then the response status should be "200"
        And the response should only contain projects with title "MATH 240"

    # ERROR FLOW
    Scenario: List all projects when none exist
        When I GET "/projects"
        Then the response status should be "200"
        And the response should contain no projects