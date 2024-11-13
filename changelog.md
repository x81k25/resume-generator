# Changelog

## [1.30]
- changed the entire project to function using Anthropic's API and not OpenAI's API
- perform extensive modifications to the input data structure
    - input responsibilities for each role are broken down into a json object containing the what, how, and result seperately
-added the changelog.md file to keep track of changes

## [1.24]
- first version included in this repository
- connects to OpenAI API to generate a resume and cover letter for the user
- restructured entire code based to be more object oriented and efficient