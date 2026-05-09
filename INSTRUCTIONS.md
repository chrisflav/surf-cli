# CLI for surfresearchcloud.nl

This repository shall contain a python CLI for interacting with surfresearchcloud.nl.
The interaction should go via their API which is documented at:

https://gw.live.surfresearchcloud.nl/v1/workspace/swagger/docs/

## Goal

The CLI needs to support all API endpoints with all parameters. Implement handling
for all listed schemas, in particular all of the data needs to be queriable from the CLI.

The API token is provided by the user as an environment variable.

## Implementation notes

- Make this an installable python package based on uv, with a proper pyproject.toml etc.
- Add tests for all features.
- Document usage in a well structured README.
- Structure the code well in subfolders and add file level documentation.
- Follow PEP8 style.
