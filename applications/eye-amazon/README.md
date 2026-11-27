# Eye Amazon

Telegram bot that tracks Amazon product prices, stores price history in MongoDB, and can send an email when a product falls below a threshold.

## Stack

- Python 3.7+
- Beautiful Soup and Requests
- MongoDB
- python-telegram-bot
- Docker and the original Heroku deployment files

## Run locally

```sh
pip install -r requirements.txt
MODE=dev TOKEN=<telegram-token> MONGO_STRING=<mongodb-uri> python bot.py
```

Mail alerts additionally use `MAIL_ID` and `PASS`. Production webhook mode also expects `HEROKU_APP_NAME` and `PORT`.

The scraper targets the Amazon page structure used when this project was written, so current pages may require selector updates.

## License

MIT
