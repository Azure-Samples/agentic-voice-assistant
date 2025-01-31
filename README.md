# Agentic Voice Assistant

Picture yourself in a busy lab, wearing thick gloves, safety goggles, and a snug lab coat. You can’t tap on a screen or use a keyboard - the gloves are too thick.

Yet you need to jot down a brilliant idea to explore later, or quickly cross check the results of another experiment.

![Laboratory as Imagined by Dall-E 3](./docs/images/laboratory.png "Laboratory as imagined by Dalle-E 3")

That’s where our Agentic Voice Assistant steps in.

It connects you and all your lab’s systems, from records and notes to instructions and data. Just talk, and it retrieves what you need, makes a note, updates a system or sends a reminder.

It works alongside you on your research, keeping you efficient and safe.

## How to use the demo

- [Deploy the demo](#how-to-deploy)
- Get UI Container App URL from the output of `azd up`
- Click on recording button or press 'P'
- Speak

### Sample Questions

- What are the personal protection instructions?
- How do I keep records in the lab?
- Give me the list of experiments.
- Update the status of experiment 3 by James Brown to Success (you can validate the record has been updated in CosmosDB experiments container)
- Summarise the record keeping instructions and send them via email to "\<your email>"

## How to deploy

### Depenendencies

- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/what-is-azure-cli): `az`
- [Azure Developer CLI](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/overview): `azd`
- [Python](https://www.python.org/about/gettingstarted/): `python`
- [UV](https://docs.astral.sh/uv/getting-started/installation/): `uv`
- Optionally [Docker](https://www.docker.com/get-started/): `docker`

### Deployment and setup

```sh
git clone https://github.com/Azure-Samples/agents-escalation.git
cd agents-escalation
azd up
```

>[!NOTE]
>Once deployed, you need to authorise the solution to use your M365 email account for the outbound email capability.
> [Authorise mail access](./docs/mail_authorisation.md)

>[!NOTE]
>AZD will also setup the local Python environment for you, using `venv` and installing the required packages.

## Architecture

![Architecture Diagram](./docs/images/architecture_v0.0.1.png)

Because the assistant has a modular architecture and powered by Azure Logic Apps, expanding its features is simple. You can add new steps and integrations without tearing everything apart.

## Contributing

This project welcomes contributions and suggestions. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for details.

## Resources

- [Chainlit Documentation](https://docs.chainlit.io/)
- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
