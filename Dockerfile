FROM python:3.9.13-slim
RUN mkdir /bot
COPY . /bot
RUN pip3 install -r /bot/requirements.txt
CMD python3 /bot/telegram_bot.py
