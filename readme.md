# PUT Thesis Tracker
## Overview
PUT Thesis Tracker is a script that monitors the USOS website of Poznan University of Technology and checks every hour for new engineering thesis topics for the Computer Science study program. If new topics are found, it sends an email notification to the user.

## Features

* Automatic monitoring of available engineering thesis topics.
* Handles CSRF token validation and submission.
* Email notifications for new topics.
* Session handling and re-login in case of session expiration.

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
   ELOGIN_LOGIN=<PUT eLogin login>
   ELOGIN_PASSWORD=<PUT eLogin passowrd>
   SENDER_EMAIL=<Your Email for Notifications>
   RECEIVER_EMAIL=<Email to Receive Notifications>
   APP_PASSWORD=<App Password for Sender Email>
   ```
   You can get your app password here: https://myaccount.google.com/apppasswords, but you need to have two-step verification enabled.

## Usage

To run the script, simply execute:

```sh
python main.py
```

To stop the program, press `Ctrl+Z`.

## License

This project is open-source under the MIT License.