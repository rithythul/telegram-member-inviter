# Telegram Client to Invite users

This program can crawl all users inside the client groups and add them to the target group. Clients should have intended permissions to add members to the target group.

- Windows
![Terminal Screenshot](/assets/images/next.windows.png)

- Linux
![Terminal Screenshot](/assets/images/next.linux.png)

# Remarks
This program acts as a telegram client and can be used to add subscribers to a target group. For channels, there are 200 subscribers limitations and only the first 200 subscribers can be invited by the admin.

# Usage
Download and run the binary file for your OS.

# Requirements

```shell
# Python 3.6.6 or higher
```

# Installation
```shell
pip install -r requirements.txt
```

# Setup API configurations
- Go to the [my telegram](https://my.telegram.org/).
- Login with a phone number.
- Click on `API development tools`.
- Create an App.
- The bot needs the `App api_id` and `App api_hash`.

# Run
```shell
python bot.py 
```
