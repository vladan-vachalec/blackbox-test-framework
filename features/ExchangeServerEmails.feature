@email
Feature: Testing feature file for MS exchange service

  Scenario Outline: User with MS exchange credentials can send an email and it stays in the mailbox
    When employee sends an email with a content from <input_file>
    Then user gets last 10 emails
    And the email is present in inbox

    Examples:
      | input_file      |
      | test_email.txt  |
      | test_email2.txt |