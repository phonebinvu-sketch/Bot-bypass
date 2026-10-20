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
  return "Bot Bypass All-in-One is Online 24/7!"


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
logger = logging.getLogger("bypass-bot")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_IDS = {
    int(x) for x in os.getenv("OWNER_IDS", "").split(",") if x.strip().isdigit()
}
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "10"))
MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", "3"))

user_cooldowns: dict[int, float] = {}
active_tasks = 0
active_lock = asyncio.Lock()


class BypassBot(commands.Bot):

  def __init__(self):
    intents = discord.Intents.default()
    super().__init__(command_prefix="!", intents=intents)

  async def setup_hook(self) -> None:
    await self.tree.sync()
    logger.info("Slash commands synced")

  async def on_ready(self) -> None:
    logger.info(f"Logged in as {self.user}")


bot = BypassBot()


# ================= GIAO DIỆN MODAL NHẬP LINK =================
class BypassModal(discord.ui.Modal):

  def __init__(self, platform_name: str):
    super().__init__(title=f"Bypass - {platform_name}")
    self.platform_name = platform_name

    self.link_input = discord.ui.TextInput(
        label="Dán đường dẫn / URL cần bypass",
        placeholder="Ví dụ: https://...",
        style=discord.TextStyle.short,
        required=True,
    )
    self.add_item(self.link_input)

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    user_link = self.link_input.value.strip()

    try:
      # Tạm thời gọi hàm core hoặc xử lý theo nền tảng
      # Bạn có thể trỏ hàm xử lý chi tiết vào đây tùy theo platform_name
      result = f"🔓 **Bypass {self.platform_name} thành công!**\n🔑 **Kết quả:** `DEMO-KEY-OR-LINK-SUCCESS`"

      embed = discord.Embed(
          title="✅ Kết quả Bypass",
          description=result,
          color=discord.Color.green(),
      )
      embed.set_footer(text=f"Yêu cầu bởi {interaction.user}")
      await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as e:
      await interaction.followup.send(
          f"❌ **Lỗi xử lý:** `{str(e)}`", ephemeral=True
      )


# ================= GIAO DIỆN CẤP 2: DANH SÁCH NÚT CHI TIẾT =================
class SubPlatformView(discord.ui.View):

  def __init__(self, region_type: str):
    super().__init__(timeout=60)
    self.region_type = region_type
    self.add_dynamic_buttons()

  def add_dynamic_buttons(self):
    if self.region_type == "vn":
      self.add_item(
          BypassButton(label="Link4M", style=discord.ButtonStyle.primary, emoji="🔗")
      )
      self.add_item(
          BypassButton(label="LinkTot", style=discord.ButtonStyle.success, emoji="📌")
      )
      self.add_item(
          BypassButton(label="YeuMoney", style=discord.ButtonStyle.danger, emoji="💰")
      )
      self.add_item(
          BypassButton(label="LayMa.net", style=discord.ButtonStyle.secondary, emoji="🇻🇳")
      )
    else:
      self.add_item(
          BypassButton(label="Delta", style=discord.ButtonStyle.success, emoji="⚡")
      )
      self.add_item(
          BypassButton(label="Work.ink", style=discord.ButtonStyle.danger, emoji="🌐")
      )
      self.add_item(
          BypassButton(label="Linkvertise", style=discord.ButtonStyle.secondary, emoji="🛡️")
      )

    # Thêm nút Quay lại menu chính
    back_btn = discord.ui.button(
        label="Quay lại", style=discord.ButtonStyle.grey, emoji="⬅️", row=4
    )
    # Gắn callback nút back
    async def back_callback(interaction: discord.Interaction):
      await interaction.response.edit_message(
          embed=getMainEmbed(), view=MainCategoryView()
      )

    back_btn.callback = back_callback
    self.add_item(back_btn)


class BypassButton(discord.ui.Button):

  def __init__(self, label: str, style: discord.ButtonStyle, emoji: str):
    super().__init__(label=label, style=style, emoji=emoji)

  async def callback(self, interaction: discord.Interaction):
    modal = BypassModal(platform_name=self.label)
    await interaction.response.send_modal(modal)


# ================= GIAO DIỆN CẤP 1: CHỌN KHU VỰC (VN / QUỐC TẾ) =================
def getMainEmbed():
  embed = discord.Embed(
      title="⚙️ Hệ thống Bypass All-in-One",
      description=(
          "Vui lòng chọn khu vực nền tảng bạn muốn vượt link ở bên dưới:"
      ),
      color=discord.Color.blue(),
  )
  embed.set_footer(text="Shoutout to Nguoibianhz | Bot hoạt động 24/7")
  return embed


class MainCategoryView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=60)

  @discord.ui.button(
      label="Nền tảng Việt Nam", style=discord.ButtonStyle.primary, emoji="🇻🇳"
  )
  async def vn_btn(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    embed = discord.Embed(
        title="🇻🇳 Nền tảng Việt Nam",
        description="Chọn dịch vụ rút gọn / traffic bên dưới:",
        color=discord.Color.green(),
    )
    await interaction.response.edit_message(
        embed=embed, view=SubPlatformView("vn")
    )

  @discord.ui.button(
      label="Nền tảng Quốc tế", style=discord.ButtonStyle.success, emoji="🌍"
  )
  async def global_btn(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    embed = discord.Embed(
        title="🌍 Nền tảng Quốc tế",
        description="Chọn dịch vụ quốc tế bên dưới:",
        color=discord.Color.orange(),
    )
    await interaction.response.edit_message(
        embed=embed, view=SubPlatformView("global")
    )


# ================= LỆNH SLASH =================
@bot.tree.command(
    name="bypass", description="Mở menu chọn khu vực và hệ thống bypass"
)
async def bypass_command(interaction: discord.Interaction) -> None:
  await interaction.response.send_message(
      embed=getMainEmbed(), view=MainCategoryView(), ephemeral=True
  )


def main() -> None:
  if not DISCORD_TOKEN:
    raise SystemExit("Missing DISCORD_TOKEN")
  keep_alive()
  bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
  main()
