# Overview

The project is managed by pyproject.toml and [uv package manager](https://docs.astral.sh/uv/getting-started/installation/).


## Local execution
For local execution init the .venv environment using [uv package manager](https://docs.astral.sh/uv/getting-started/installation/):

```shell
cd src/chainlit
uv sync
. ./.venv/bin/activate
chainlit run ./chat.py
```
## Environment variables

The local execution relies on environmental variables to reference Azure resources required - specifically the model.

These environment vaiables are set automatically by `azd` when the infrastructure is provisioned by `azd up`. 

They are set in the AZD env file: `$project/.azure/<selected_azd_environment>/.env`

When `chainlit` command is run, the application looks up and reads the `.env` file above automatically.