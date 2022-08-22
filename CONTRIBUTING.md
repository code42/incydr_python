# Contributing
A brief contributing guide for the Incydr python SDK.

Examples of all the steps documented  here can be found in the existing clients.

## Adding a client


- Create a `_client_name/` folder within the `incydr` package.
  - Create a `client.py` and `models.py` module within this folder.
- Create pydantic models from the OpenAPI specs for the desired client.
  - The [datamodel-code-generator project](https://pydantic-docs.helpmanual.io/datamodel_code_generator/) can be used to generate these models.
  - Organize the appropriate models into your `/_client_name/models.py` module, adjusting descriptions and type checking as necessary.
  - Any enums that will be needed by end-users should go into the `incydr/enums/models.py` module.
- Create a class for your client (`class ClientName`) with a version property (ex: `v1`)
- Create a versioned class for your client (`class ClientNameV1`) accessible through the previously defined version property.
- Create methods for wrapping the desired API calls within the versioned client class.
- Tests for the client should be added into the tests package within `/tests/test_client_name.py`.
  - Run tests with `hatch run test:cov`
- Run the style linter with `hatch run style:check`

## Documenting a client

- Add the appropriate docstrings to the models and methods for your client.
- Import response models and add them to the `__all__` definition in the `/incydr/models.py` module.
- Adds those models to the `/docs/models.md` file with the appropriate header(s).
- Add a `client_name.md` to the `docs/` directory and add the following to generate documentation from the method docstrings (replace the ClientName with your client's class name):

```markdown
::: incydr._devices.client.ClientNameV1
    :docstring:
    :members:
```

- Add your `client_name.md` file to the `nav` section of the `mkdocs.yml` config file.
