# Changelog

## [1.3.3]
- added new functions to ensure that json outputs are properly formatted
- added error handling if objects are not properly formatted
- added new model prompt to verify that all experiences are indeed from the original user data json file
- added explict function name to all error handling
- add output at the initiation of each generate_resume sub-chat-completion function

## [1.32]
- moved prompts from inside the body of the src-core code to the model config files to more easily track how prompts are evolving through the iterations
- started to make accommodations for the Anthropic API 'overloaded_errors' to pause and retry pipeline instead of failing

## [1.31]
- add added multi-threading on API calls that can be made simultaneously
- added function to automatically generate the list of hard skills
- due to the introduction of the automatic hard skills insertion, well de-emphasize hard skills in the responsibilities section

## [1.30]
- changed the entire project to function using Anthropic's API and not OpenAI's API
- perform extensive modifications to the input data structure
    - input responsibilities for each role are broken down into a json object containing the what, how, and result separately
- added the changelog.md file to keep track of changes

## [1.24]
- first version included in this repository
- connects to OpenAI API to generate a resume and cover letter for the user
- restructured entire code based to be more object-oriented and efficient