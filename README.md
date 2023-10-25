# Telegram User Inviter

[![Build binary file](https://github.com/mjavadhpour/telegram-member-inviter/actions/workflows/build.yml/badge.svg)](https://github.com/mjavadhpour/telegram-member-inviter/actions/workflows/build.yml)

Telegram Member Inviter is a program designed to generate a list of users within client groups and adds them into a target group. However, the client must possess the necessary permissions to execute the user addition process for the target group.

- Windows
![Terminal Screenshot](/assets/images/next.windows.png)

- Linux
![Terminal Screenshot](/assets/images/next.linux.png)

# Remarks
This tool operates as a Telegram client that enables users to grow their Telegram groups by adding members from other client groups. However, note that when dealing with channels, the tool can only invite the first 200 subscribers, as these are the only ones accessible to the admin.

# Getting Started
You can download and run the binary file based on your OS from [releases](https://github.com/mjavadhpour/telegram-member-inviter/releases/latest).
The application relies on API configurations that need to be set manually:
- Open [my telegram](https://my.telegram.org/).
- Login with a phone number.
- Click on `API development tools`.
- Create an App.
- The bot needs the `App api_id` and `App api_hash`.

For any other usage directly using the script:
## Prerequisites

#### Python 3.11 or later
To replicate this tool on your systems, ensure that you have Python 3.11 or a later version installed. I recommend setting up a virtual environment using "venv" to enhance the Python environment's effectiveness.
To set up the Python virtual environment on your system, run the following lines of code:
```shell
# In the project directory
python -m venv .venv
. .venv/bin/activate 
pip install .
```

#### Conda
Also You can use conda to manage the Python version and dependencies for this project. Conda allows you to create isolated Python environments with specific package versions installed. This helps ensure you have the correct dependencies for the project without impacting your system Python installation.

To create a conda environment and install the requirements:

```shell
# In the project directory
# create a conda environment local to the project
conda create -p ./.env python=3.12 -y
conda activate ./.env
pip install .
```
Then you can run the project within the conda environment:

```shell
conda activate ./.env
```
Using conda environments helps avoid dependency conflicts and makes it easier to replicate the exact environment needed for the project.

## Run
```shell
# In the project directory
python .
```
