from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime
from loguru import logger

from app.services.ingestion.zip_parser import ParsedMessage, IngestionResult


class SlackClient:
    """Slack API client for fetching data"""

    def __init__(self, access_token: str):
        self.client = WebClient(token=access_token)

    async def fetch_all_data(self) -> IngestionResult:
        """
        Fetch all public channels + user info.
        Returns IngestionResult with messages.
        """
        result = IngestionResult()
        user_cache = {}

        try:
            channels_result = await self._get_channels()
            for channel_id, channel_name in channels_result:
                await self._fetch_channel_messages(channel_id, channel_name, result, user_cache)

            logger.info(f"✅ Slack sync complete: {len(result.messages)} messages from {len(channels_result)} channels")

        except SlackApiError as e:
            result.errors.append(f"Slack API error: {str(e)}")
            logger.error(f"Slack API error: {str(e)}")

        return result

    async def _get_channels(self) -> list:
        """Fetch all public channels"""
        channels = []
        try:
            response = self.client.conversations_list(types="public_channel", limit=100)
            for channel in response.get("channels", []):
                channels.append((channel["id"], channel["name"]))
        except SlackApiError as e:
            logger.error(f"Error fetching channels: {str(e)}")

        return channels

    async def _fetch_channel_messages(
        self,
        channel_id: str,
        channel_name: str,
        result: IngestionResult,
        user_cache: dict
    ):
        """Fetch all messages from a channel"""
        try:
            cursor = None
            count = 0

            while True:
                response = self.client.conversations_history(
                    channel=channel_id,
                    limit=100,
                    cursor=cursor
                )

                for msg in response.get("messages", []):
                    if msg.get("type") != "message" or msg.get("subtype"):
                        continue

                    text = msg.get("text", "").strip()
                    if not text or len(text) < 5:
                        continue

                    ts_raw = msg.get("ts", "0")
                    try:
                        ts = datetime.fromtimestamp(float(ts_raw))
                    except (ValueError, OSError):
                        ts = datetime.utcnow()

                    slack_user_id = msg.get("user", "")

                    if slack_user_id and slack_user_id not in user_cache:
                        try:
                            user_info = self.client.users_info(user=slack_user_id)
                            real_name = (
                                user_info.get("user", {})
                                .get("real_name")
                            )
                            user_cache[slack_user_id] = (
                                real_name or slack_user_id
                            )
                        except Exception:
                            user_cache[slack_user_id] = slack_user_id

                    sender_name = user_cache.get(
                        slack_user_id,
                        slack_user_id
                    )

                    parsed = ParsedMessage(
                        source="slack",
                        external_id=ts_raw,
                        sender_raw=sender_name,
                        channel_or_thread=channel_name,
                        content=text,
                        timestamp=ts,
                    )

                    result.messages.append(parsed)
                    count += 1

                cursor = response.get(
                    "response_metadata",
                    {}
                ).get("next_cursor")

                if not cursor:
                    break

            result.file_summary.append(
                f"#{channel_name} → {count} messages"
            )

        except SlackApiError as e:
            error_msg = (
                f"Error fetching messages from "
                f"#{channel_name}: {str(e)}"
            )
            result.errors.append(error_msg)
            logger.error(error_msg)
