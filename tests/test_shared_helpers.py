"""Transport boundaries and credential parsing, with no live communication."""
from pathlib import Path
import tempfile
import unittest

from comms.discord_bot import HelixDiscordBot
from comms.slack_bot import HelixSlackBot
from comms.telegram_bot import HelixTelegramBot
from comms.webhook_channel import HelixWebhookChannel
from comms.whatsapp_bot import HelixWhatsAppBot
from comms.message_chunks import chunk_message
from core.credentials import read_credentials


class SharedHelperTests(unittest.TestCase):
    def test_channel_limits_and_existing_five_chunk_ceiling_survive(self):
        for channel, limit in ((HelixDiscordBot, 1900), (HelixSlackBot, 3000),
                               (HelixTelegramBot, 4000), (HelixWebhookChannel, 4000), (HelixWhatsAppBot, 4096)):
            with self.subTest(channel=channel.__name__):
                self.assertEqual(channel._chunk_message(""), [""])
                self.assertEqual(channel._chunk_message("x" * limit), ["x" * limit])
                self.assertEqual(channel._chunk_message("x" * (limit + 1)), ["x" * limit, "x"])
                self.assertEqual(channel._chunk_message("x" * (6 * limit)), ["x" * limit] * 5)

    def test_paragraph_newline_and_unicode_boundaries_are_unchanged(self):
        self.assertEqual(chunk_message("abcdef\n\nghijkl", 10), ["abcdef", "ghijkl"])
        self.assertEqual(chunk_message("abcde\nfghijk", 10), ["abcde", "fghijk"])
        self.assertEqual(chunk_message("星" * 11, 10), ["星" * 10, "星"])

    def test_credentials_preserve_equal_signs_quotes_comments_and_duplicate_precedence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "credentials.env"
            self.assertEqual(read_credentials(path), {})
            self.assertFalse(path.exists())
            content = '# ignored=x\n KEY = "first"\nKEY="last=a=b"\nSINGLE=\'literal\'\nignored\n'
            path.write_text(content)
            self.assertEqual(read_credentials(path), {"KEY": "last=a=b", "SINGLE": "'literal'"})
            self.assertEqual(path.read_text(), content)
