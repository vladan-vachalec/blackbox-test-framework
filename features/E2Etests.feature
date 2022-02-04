Feature: I want to have a whole system E2E scenarios including metrics in Prometheus

  @e2e @monitoring
  Scenario Outline: Employee sends an email and an incident is created in Symantec DLP
    When employee sends an email with a content from <input_file>
    And a DLP Incident with some severity will be generated
    Then the generated incidents contain correct values (<expected_status>, <expected_nr_matches>, <expected_severity>)

    Examples:
      | input_file  | expected_status | expected_nr_matches | expected_severity |
      | IBAN-CH.txt | new             | 9                   | low               |

  @e2e @monitoring
  Scenario Outline: Someone executes an SQL query in a database which triggers an event in Splunk
    When a user connects to a <db_type> database with following credentials <credentials>
    And executes a <query> on the <db_type> database
    Then an admin checks if an event has been created in Splunk


    Examples:
      | db_type | credentials     | query                                                                     |
      | MSSQL   | admin:test123   | SELECT * FROM users WHERE username = 'administrator'--' AND password = '' |
      | ORACLE  | ora:supersecret | SELECT * FROM users WHERE username = 'administrator'--' AND password = '' |


  @e2e @monitoring
  Scenario Outline: User logs via UI to an email service and sends an email which generates an event in Splunk
    When a user opens a page <url>
    And logs into the website
    And user gets last <refresh_count> emails
    And refreshes the pages <refresh_count> times
    Then an admin checks if an event has been created in Splunk


    Examples:
      | url                                   | refresh_count |
      | https://myinbucketinstance/mymailbox  | 1             |
      | https://myinbucketinstance/mymailbox2 | 10            |


