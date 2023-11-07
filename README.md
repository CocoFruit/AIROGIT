# AIROGIT 

![Git Meme](./images/git_meme.webp)

**AIROGIT** (*AI-Related Overview and Git Information Tool*) is an innovative tool designed to simplify and enhance your Git version control workflow. Our ultimate goal is to empower developers with automated commit messages and descriptions using advanced Language Model technology. This ensures that your Git history is clear, informative, and consistent. AIROGIT seamlessly integrates with [GIT-COLA's Git GUI](https://github.com/git-cola/git-cola), making it the ultimate solution for streamlining your versioning process.

## Features

- **LLM-Powered Commit Messages**: AIROGIT leverages cutting-edge Language Model technology to analyze your code changes and generate meaningful commit messages and descriptions.

- **Efficiency and Consistency**: Say goodbye to the hassle of manual commit message creation. AIROGIT promotes consistency, reduces confusion, and ensures your commit messages are well-formed.

- **Seamless GIT-COLA Integration**: AIROGIT seamlessly integrates into [GIT-COLA's Git GUI](https://github.com/git-cola/git-cola), offering a familiar and user-friendly experience for developers.

## Project Overview

AIROGIT is designed to enhance the Git version control workflow by automating the process of generating commit messages and descriptions. This repository contains the source code and documentation for AIROGIT.

## Demo
[AIROGIT Demo](https://www.youtube.com/watch?v=zMMak_UV_bU)

## Getting Started

### Prerequisites

Before you begin, ensure you have the following prerequisites installed:

- [Python 3.x](https://www.python.org/downloads/)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/CocoFruit/AIROGIT.git
```
Or
downloading the zip file and extract it.

2. Navigate to the project directory and be sure to be in the /airogit/airogit directory

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Install the package:

```bash
pip install .
```

### Configuration

Before you start using AIROGIT, make sure to set up your API key by following these steps:

*Note: You can obtain your API key from OpenAI's official website. Keep your API key secure and do not share it publicly or with untrusted parties.*

1. Navigate to the `airogit\cola` directory within your project directory.

2. Locate the `config.yaml` file.

3. Open `config.yaml` using a text editor.

4. Find the section for API Key and add your API key as follows:
   ```yaml
   api_key: YOUR_API_KEY
   ```
5. Save and close the `config.yaml` file.

**Keep your API key secure and do not share it publicly or with untrusted parties.**

### Usage

Now that you have AIROGIT installed, be sure you are in the directory of the git project you want to use AIROGIT with. Then, run the following command:

```bash
git-cola
```

or

```bash
cola
```

## Project Status

AIROGIT is actively maintained and developed by me and the [GIT-COLA](https://github.com/git-cola/git-cola) is also being actively maintaned and developed seperately. We welcome contributions from the community and are committed to improving this tool continuously.

### Repository Structure

#### Git Cola Source Code: 
- `bin/`: Binary files and executables.
- `cola/`: Code related to GIT-COLA integration.
- `contrib/`: Contributed code and scripts.
- `docs/`: Documentation for AIROGIT.
- `extras/`: Additional resources and files.
- `git-cola-full/`: Git-COLA source code.
- `qtpy/`: Code related to QtPy.
- `requirements/`: Requirement files for the project.
- `share/`: Shared files and resources.
- `test/`: Test-related code and files.
- `.gitignore`: Git ignore configuration.
- `.mailmap`: Mailmap file.
- `.pre-commit-config.yaml`: Configuration for pre-commit hooks.
- `.pylintrc`: PyLint configuration file.
- `.readthedocs.yml`: Configuration for ReadTheDocs.
- `CHANGES.rst`: Release change log.
- `CONTRIBUTING.md`: Guidelines for contributing to the project.
- `COPYING`: Copying/license information.
- `COPYRIGHT`: Copyright information.
- `LICENSE`: Project license.
- `Makefile`: Makefile for project tasks.
- `__init__.py`: Initialization file.
- `garden.yaml`: Configuration for garden.
- `pynsist.cfg`: Configuration for PyNsiSt.
- `pyproject.toml`: Project metadata in TOML format.
- `pytest.ini`: Configuration for PyTest.
- `resources.md`: Information about project resources.
- `setup.cfg`: Setup configuration.
- `setup.py`: Setup script for installation.
- `tox.ini`: Configuration for Tox testing.

#### AIROGIT Source Code:
- `README.md`: This documentation file.
- `git_meme.webp`: Fun Git meme image.
- `TODO.md`: Task list and project TODOs.
- `airogit.py`: AIROGIT source code.
- `commit_template.txt`: Commit message template.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
