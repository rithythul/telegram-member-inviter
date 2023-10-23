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
To replicate this tool on your systems, ensure that you have Python 3.11 or a later version installed. I recommend setting up a virtual environment using "venv" to enhance the Python environment's effectiveness.
To set up the Python virtual environment on your system, run the following lines of code:
```shell
python -m venv .venv
. .venv/bin/activate 
pip install .
```

## Run
```shell
# In the project directory
python .
```
