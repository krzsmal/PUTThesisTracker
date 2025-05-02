# PUT Thesis Tracker
## Overview
PUT Thesis Tracker is a Python script that monitors the USOS system of Poznan University of Technology and checks for new engineering thesis topics in the Computer Science study program. The script runs at configurable times throughout the day and sends email notifications when new topics are detected.

## Features

* Automatic periodic monitoring of available engineering thesis topics.
* Supports multiple configurable check times per day.
* Handles CSRF token validation and submission.
* Email notifications for new topics.
* Session handling and re-login in case of session expiration.
* Persistent topic storage using JSON file.
* Logging of activity and error messages for debugging.

## Installation

1. **Clone the repository**:
   ```sh
   git clone https://github.com/krzsmal/PUTThesisTracker.git
   cd PUTThesisTracker
   ```

2. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory with the following content:
   ```env
   ELOGIN_LOGIN=<Your PUT eLogin username>
   ELOGIN_PASSWORD=<Your PUT eLogin password>
   SENDER_EMAIL=<Your email address for sending notifications>
   RECEIVER_EMAIL=<Recipient email address for notifications>
   APP_PASSWORD=<App-specific password for the sender email>
   SMTP_SERVER=<SMTP server address>                           # Optional, default: smtp.gmail.com
   SMTP_PORT=<SMTP server port>                                # Optional, default: 587
   CHECK_TIMES=<Comma-separated times in 24h format>           # Optional, default: 09:00,12:00,15:00,21:00,00:00
   SEND_INITIAL_EMAILS=<True/False>                            # Optional, send all existing topics on first run
   ```
   If you are using Gmail, you can get your app password here: https://myaccount.google.com/apppasswords, but you need to have two-step verification enabled.

## Usage

To run the script, simply execute:

```sh
python main.py
```
It will run continuously and check for new topics at the times specified in `.env`. Newly detected topics will be saved in `topics.json`.

To stop the program, press `Ctrl+C`.

## License

This project is open-source under the MIT License.