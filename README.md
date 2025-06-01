# target-starrocks

`target-starrocks` is a Singer target for Starrocks querying Apache Iceberg.

Build with the [Meltano Target SDK](https://sdk.meltano.com).

**❗ Important Note: This project is currently a Work In Progress (WIP) and relies heavily on the default `SQLSink` and `SQLTarget` implementations from the Meltano SDK. Functionality may be limited.**

**❗ This target includes workarounds for certain limitations in the `starrocks` Python connector, specifically concerning Iceberg table creation and VARCHAR length requirements. While these workarounds aim to provide a smoother experience, it's important to be aware of the underlying issues with the connector. For more details on the original connector issue, see [GitHub Issue #59463](https://github.com/StarRocks/starrocks/issues/59463).**

This target has been developed with the assumption that StarRocks is being used as a query engine for Apache Iceberg, leveraging a REST catalog. While this is the primary design consideration, the project is open to contributions. If you have a different use case or improvements, feel free to fork the repository and submit a pull request!

## Installation

This target is intended to be used with [Meltano](https://meltano.com/).

Since `target-starrocks` is not yet published on PyPI, you need to install it directly from its Git repository.

1.  **Ensure the Starrocks python connector is installed in your project `poetry add starrocks`**

2.  **Ensure Meltano is installed.** If you haven't already, [install Meltano](https://docs.meltano.com/getting-started/installation).

3.  **Add the target to your Meltano project:**
    Open your `meltano.yml` file and add the following under the `plugins.loaders` section (or `plugins.targets` if you are on an older Meltano version). Adjust the `pip_url` to point to the desired branch or commit if necessary.

    ```yaml
    plugins:
      loaders:
        - name: target-starrocks
          namespace: target_starrocks
          pip_url: git+https://github.com/polarlabsdev/target-starrocks.git # Or your fork/branch
          capabilities:
            - about
            - stream-maps
            - schema-flattening
          settings:
            - name: host
              value: "your-starrocks-fe-host-or-ip"
            - name: port
              value: 9030
            - name: user
              value: "your-starrocks-user"
            - name: password
              kind: password
              sensitive: true
              value: "your-starrocks-password"
            - name: catalog
              value: "your_iceberg_catalog_name"
            - name: warehouse
              value: "your_warehouse_or_database_name"
    ```

4.  **Install the plugin:**
    Run the following command in your Meltano project directory:
    ```bash
    meltano install loader target-starrocks
    ```

    This will install `target-starrocks` and its dependencies, including the `starrocks` Python connector, into your Meltano project's environment.

## Configuration

### Accepted Config Options

A full list of supported settings and capabilities for this
target is available by running:

```bash
target-starrocks --about
```

### Configure using environment variables

This Singer target will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Authentication and Authorization

## Usage

You can easily run `target-starrocks` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Target Directly

```bash
target-starrocks --version
target-starrocks --help
# Test using the "Smoke Test" tap:
tap-smoke-test | target-starrocks --config /path/to/target-starrocks-config.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

Prerequisites:

- Python 3.9+
- [Poetry](https://python-poetry.org/)

```bash
poetry install
```

### Create and Run Tests

Create tests within the `tests` subfolder and
then run:

```bash
poetry run pytest
```

You can also test the `target-starrocks` CLI interface directly using `poetry run`:

```bash
poetry run target-starrocks --help
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the Meltano Singer SDK to
develop your own Singer taps and targets.
