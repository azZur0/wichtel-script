# 🎄 Secret Santa (Wichtel) Matching Script

A Python script that helps organize Secret Santa gift exchanges with couple constraints, while keeping assignments secret even from the organizer!

## Features

- ✅ Automatic matching that ensures everyone gives and receives exactly one gift
- ✅ Couple constraints: Partners won't be matched to each other
- ✅ Secret notifications via email - even you won't know who has whom!
- ✅ Dry-run mode to test without sending emails
- ✅ Configurable email templates
- ✅ Validates matching forms a complete cycle (no short loops)

## Requirements

- Python 3.6 or higher
- An email account for sending notifications (Gmail, Outlook, etc.)

## Installation

1. Clone or download this script
2. No additional Python packages needed - uses only standard library!

## Setup

### 1. Create Your Configuration File

Copy the example configuration:

```bash
cp config.example.json config.json
```

### 2. Edit the Configuration

Edit `config.json` with your participants and email settings:

```json
{
  "participants": [
    {
      "name": "Alice",
      "email": "[email protected]"
    },
    {
      "name": "Bob",
      "email": "[email protected]"
    }
  ],
  "couples": [
    ["Alice", "Bob"]
  ],
  "email_config": {
    "from_email": "[email protected]",
    "password": "your-app-password",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "subject": "🎄 Your Secret Santa Assignment",
    "message_template": "Hello {giver},\n\nYou are the Secret Santa for: {receiver}\n\nHappy gifting! 🎁\n"
  }
}
```

#### Configuration Fields:

- **participants**: List of people participating
  - `name`: Person's name
  - `email`: Their email address

- **couples**: List of couples (pairs who shouldn't be matched together)
  - Each couple is a 2-element array with the names of both people

- **email_config**: Email settings for sending notifications
  - `from_email`: Your email address
  - `password`: Your email password or app-specific password
  - `smtp_server`: SMTP server (Gmail: smtp.gmail.com, Outlook: smtp-mail.outlook.com)
  - `smtp_port`: Usually 587 for TLS
  - `subject`: Email subject line
  - `message_template`: Email body with `{giver}` and `{receiver}` placeholders

### 3. Setup Email Account

#### For Gmail:

1. Enable 2-factor authentication on your Google account
2. Generate an "App Password":
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password
3. Use this app password in your config (not your regular Gmail password)

#### For Outlook/Hotmail:

1. Use your regular password
2. SMTP server: `smtp-mail.outlook.com`
3. Port: `587`

#### For Other Providers:

Search for "[your provider] SMTP settings" to find the correct server and port.

## Usage

### Test Run (Recommended First!)

Test the configuration without sending emails:

```bash
python3 wichtel.py config.json --dry-run
```

This will show you what emails would be sent without actually sending them.

### Run for Real

Once you've tested, run it for real:

```bash
python3 wichtel.py config.json
```

⚠️ **Important**: Once you run this command, the emails will be sent immediately, and you won't see the matching! This is by design to keep it secret.

### Advanced Options

```bash
# Use a specific random seed (for testing/reproducibility)
python3 wichtel.py config.json --seed 42

# Combine options
python3 wichtel.py config.json --dry-run --seed 42
```

## How It Works

1. **Validation**: Checks that your configuration is valid
2. **Matching Algorithm**:
   - Randomly shuffles participants
   - Ensures no one gets themselves
   - Ensures couples don't get each other
   - Verifies the matching forms one complete cycle
   - Retries if constraints can't be satisfied
3. **Notification**: Sends individual emails to each participant with their assignment
4. **Privacy**: The script never displays the matching - it goes directly from generation to email sending

## Troubleshooting

### "Authentication failed" error

- Make sure you're using an app-specific password (not your regular password) for Gmail
- Check that your email and password are correct
- Verify 2-factor authentication is enabled (required for Gmail app passwords)

### "Could not find valid matching" error

- This happens if constraints are impossible to satisfy
- Make sure you have at least 3 participants
- If you have many couples, you might need more single participants

### Email not received

- Check spam/junk folders
- Verify email addresses are correct in config
- Try the `--dry-run` flag to see what would be sent
- Some email providers have daily sending limits

## Security Notes

- Store your `config.json` securely (it contains your email password!)
- Add `config.json` to `.gitignore` if using version control
- Delete the config file after running if you want to ensure no one can see the participant list

## Example Scenarios

### Scenario 1: Small Group

3 singles, 1 couple (5 people total) - works perfectly!

### Scenario 2: Mostly Couples

2 couples, 2 singles (6 people total) - works great!

### Scenario 3: All Couples

3 couples (6 people total) - works fine as long as you have at least 3 couples!

## License

Free to use and modify!

## Questions?

The script includes helpful error messages. If something goes wrong, read the error message carefully - it usually tells you exactly what to fix!