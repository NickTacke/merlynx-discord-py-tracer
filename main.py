from __future__ import annotations

import asyncio
import json
import os

import discord
import merlynx

SCHEMA = merlynx.define_config(
    tracer_value=merlynx.string_field(label="Ticket #283 tracer value")
)


class TracerBot(discord.Client):
    config: merlynx.MerlynxConfig

    async def setup_hook(self) -> None:
        self.config = await merlynx.connect(schema=SCHEMA)

    async def on_ready(self) -> None:
        guild_id = os.environ["EVIDENCE_GUILD_ID"]
        if self.get_guild(int(guild_id)) is None:
            raise RuntimeError("Discord Gateway did not report the evidence Guild")

        expected = os.environ.get("EVIDENCE_EXPECTED_VALUE")
        value = self.config.get(guild_id, "tracer_value")
        if expected is not None and value != expected:
            raise RuntimeError("the initial Config snapshot did not contain the expected tracer value")

        self.config.report_gateway("connected")
        print(
            json.dumps(
                {
                    "event": "issue_283_snapshot_read",
                    "gatewayUserId": str(self.user.id) if self.user else None,
                    "guildId": guild_id,
                    "key": "tracer_value",
                    "matchedExpected": expected is not None and value == expected,
                }
            ),
            flush=True,
        )

    async def on_disconnect(self) -> None:
        self.config.report_gateway("disconnected")


asyncio.run(
    TracerBot(intents=discord.Intents.default()).start(os.environ["DISCORD_TOKEN"])
)