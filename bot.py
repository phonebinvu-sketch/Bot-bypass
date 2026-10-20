from __future__ import annotations

import asyncio
import logging
import os
import re
from typing import Optional
import threading
from flask import Flask

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from core import get_key

load_dotenv()

# --- MÁY CHỦ WEB GIẢ LẬP ĐỂ GIỮ PORT TRÊN RENDER (24/7) ---
app = Flask("")


@app.route("/")
def home():
  return "PlatoRelay Bot is Online 24/7!"


def run_web():
  app.run(host="0.0.0.0", port=8080)


def keep_alive():
  t = threading.Thread(target=run_web)
  t.start()


# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("plato-bot")

# Config
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_IDS = {
    int(x) for x in os.getenv("OWNER_IDS", "").split(",") if x.strip().isdigit()
}
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "30"))
MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", "3"))

# Rate limiting
user_cooldowns: dict[int, float] = {}
active_tasks = 0
active_lock = asyncio.Lock()

URL_REGEX = re.compile(
    r"https?://(?:auth\.)?platorelay\.com/[^\s]+",
    re.IGNORECASE,
)


class PlatoBot(commands.Bot):

  def __init__(self):
    intents = discord.Intents.default()
    intents.message_content = True
    super().__init__(command_prefix="!", intents=intents)
    self.tree = app_commands.CommandTree(self)

  async def setup_hook(self) -> None:
    await self.tree.sync()
    logger.info("Slash commands synced")

  async def on_ready(self) -> None:
    logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
    await self.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="/bypass | PlatoRelay",
        )
    )


bot = PlatoBot()


def is_valid_plato_url(url: str) -> bool:
  return bool(URL_REGEX.search(url))


async def run_bypass(
    url: str, progress_msg: Optional[discord.Message] = None
) -> str:
  """Run get_key in a thread so it doesn't block the event loop."""
  loop = asyncio.get_running_loop()
  logs: list[str] = []

  def verbose_cb(msg: str) -> None:
    logs.append(msg)
    logger.info(msg)

  result = await loop.run_in_executor(
      None, lambda: get_key(url, verbose_cb=verbose_cb)
  )
  return result


@bot.tree.command(
    name="bypass", description="Bypass PlatoRelay link and get the key"
)
@app_commands.describe(url="PlatoRelay auth URL (must contain ticket)")
async def bypass_command(interaction: discord.Interaction, url: str) -> None:
  global active_tasks

  # Basic validation
  url = url.strip()
  if not is_valid_plato_url(url):
    await interaction.response.send_message(
        "❌ URL không hợp lệ. Cần link từ `auth.platorelay.com`.",
        ephemeral=True,
    )
    return

  user_id = interaction.user.id
  now = asyncio.get_event_loop().time()

  # Cooldown
  if user_id not in OWNER_IDS:
    last = user_cooldowns.get(user_id, 0)
    remaining = COOLDOWN_SECONDS - (now - last)
    if remaining > 0:
      await interaction.response.send_message(
          f"⏳ Vui lòng đợi **{remaining:.0f}s** trước khi dùng lại.",
          ephemeral=True,
      )
      return

  # Concurrent limit
  async with active_lock:
    if active_tasks >= MAX_CONCURRENT and user_id not in OWNER_IDS:
      await interaction.response.send_message(
          f"🚦 Bot đang xử lý quá nhiều request ({active_tasks}/{MAX_CONCURRENT})."
          " Thử lại sau.",
          ephemeral=True,
      )
      return
    active_tasks += 1

  user_cooldowns[user_id] = now

  await interaction.response.defer(thinking=True, ephemeral=True)

  try:
    embed = discord.Embed(
        title="🔄 Đang bypass...",
        description=f"```\n{url[:80]}...\n```",
        color=discord.Color.blue(),
    )
    embed.set_footer(text=f"Requested by {interaction.user}")
    status_msg = await interaction.followup.send(embed=embed, ephemeral=True)

    result = await run_bypass(url)

    if result and not result.startswith("bypass fail"):
      success_embed = discord.Embed(
          title="✅ Bypass thành công!",
          color=discord.Color.green(),
      )
      success_embed.add_field(
          name="Key", value=f"```\n{result}\n```", inline=False
      )
      success_embed.set_footer(text=f"Requested by {interaction.user}")
      await status_msg.edit(embed=success_embed)
    else:
      fail_embed = discord.Embed(
          title="❌ Bypass thất bại",
          description=f"```\n{result}\n```",
          color=discord.Color.red(),
      )
      fail_embed.set_footer(text=f"Requested by {interaction.user}")
      await status_msg.edit(embed=fail_embed)

  except Exception as e:
    logger.exception("Bypass error")
    await interaction.followup.send(f"❌ Lỗi nội bộ: `{e}`", ephemeral=True)
  finally:
    async with active_lock:
      active_tasks = max(0, active_tasks - 1)


@bot.tree.command(name="ping", description="Check bot latency")
async def ping_command(interaction: discord.Interaction) -> None:
  latency = round(bot.latency * 1000)
  await interaction.response.send_message(
      f"🏓 Pong! `{latency}ms`", ephemeral=True
  )


@bot.tree.command(name="status", description="Bot status & concurrent jobs")
async def status_command(interaction: discord.Interaction) -> None:
  embed = discord.Embed(title="📊 Bot Status", color=discord.Color.blurple())
  embed.add_field(name="Active jobs", value=str(active_tasks), inline=True)
  embed.add_field(name="Max concurrent", value=str(MAX_CONCURRENT), inline=True)
  embed.add_field(name="Cooldown", value=f"{COOLDOWN_SECONDS}s", inline=True)
  embed.add_field(
      name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True
  )
  await interaction.response.send_message(embed=embed, ephemeral=True)


def main() -> None:
  if not DISCORD_TOKEN:
    raise SystemExit("Missing DISCORD_TOKEN in environment / .env")
  keep_alive()  # Kích hoạt luồng Flask mở cổng 8080 cho Render
  bot.run(DISCORD_TOKEN, log_handler=None)


if __name__ == "__main__":
  main()
