import os

# Must be set before config.py is imported (happens at collection time)
os.environ.setdefault("TWITCH_BOT_TOKEN", "oauth:test_token")
os.environ.setdefault("TWITCH_BOT_NICK", "TestBot")
os.environ.setdefault("TWITCH_CHANNEL", "testchannel")
os.environ.setdefault("ADMIN_KEY", "test_admin_key")
