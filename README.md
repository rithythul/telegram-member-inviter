# Telegram Client to Invite users

This program can crawl all users inside the client groups and add them to the target group. Clients should have intended permissions to add members to the target group.

- Windows
![Terminal Screenshot](/assets/images/next.windows.png)

- Linux
![Terminal Screenshot](/assets/images/next.linux.png)

- Mac
![Terminal Screenshot](/assets/images/next.mac.png)

# Remarks
This program act as a telegram client, at the time that it developed, telegram doesn't have limitations to add subscribers to a group by the admin, but currently telegram add a limitations for this purpose, so only first 200 members can be added by the admin of the group and another one should be invited by the invitation link.

# Requirements

```shell
# Python 3.6.6 or higher
```

# Installation
```shell
pip install -r requirements.txt
```

# Setup API configurations
- Got to the [my telegram](https://my.telegram.org/).
- Login with a phone number.
- Click on `API development tools`.
- Create an App.
- The bot need the `App api_id` and `App api_hash`.

# Run
```shell
python bot.py 
```
