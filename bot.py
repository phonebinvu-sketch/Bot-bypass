from __future__ import annotations

import asyncio
import logging
import os
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
      loop = asyncio.get_running_loop()
      result = await loop.run_in_executor(None, lambda: get_key(user_link))

      if result and not str(result).startswith("bypass fail"):
        success_embed = discord.Embed(
            title=f"✅ Bypass {self.platform_name} thành công!",
            color=discord.Color.green(),
        )
        success_embed.add_field(
            name="Kết quả (Key/Link)", value=f"```\n{result}\n```", inline=False
        )
        success_embed.add_field(
            name="Link gốc", value=f"`{user_link}`", inline=False
        )
        success_embed.set_footer(text=f"Yêu cầu bởi {interaction.user}")
        await interaction.followup.send(embed=success_embed, ephemeral=True)
      else:
        fail_embed = discord.Embed(
            title="❌ Bypass thất bại",
            description=f"```\n{result}\n```",
            color=discord.Color.red(),
        )
        fail_embed.set_footer(text=f"Yêu cầu bởi {interaction.user}")
        await interaction.followup.send(embed=fail_embed, ephemeral=True)

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
          BypassButton(
              label="Link4M", style=discord.ButtonStyle.primary, emoji="🔗"
          )
      )
      self.add_item(
          BypassButton(
              label="LinkTot", style=discord.ButtonStyle.success, emoji="📌"
          )
      )
      self.add_item(
          BypassButton(
              label="YeuMoney", style=discord.ButtonStyle.danger, emoji="💰"
          )
      )
      self.add_item(
          BypassButton(
              label="LayMa.net", style=discord.ButtonStyle.secondary, emoji="🇻🇳"
          )
      )
    else:
      self.add_item(
          BypassButton(
              label="Delta", style=discord.ButtonStyle.success, emoji="⚡"
          )
      )
      self.add_item(
          BypassButton(
              label="Work.ink", style=discord.ButtonStyle.danger, emoji="🌐"
          )
      )
      self.add_item(
          BypassButton(
              label="Linkvertise",
              style=discord.ButtonStyle.secondary,
              emoji="🛡️",
          )
      )

    back_btn = discord.ui.Button(
        label="Quay lại", style=discord.ButtonStyle.grey, emoji="⬅️", row=4
    )

    async def back_callback(interaction: discord.Interaction):
      await interaction.response.defer(ephemeral=True)
      embed = discord.Embed(
          title="⚙️ Hệ thống Bypass Tự động",
          description=(
              "Vui lòng chọn khu vực nền tảng bạn muốn vượt link ở bên dưới:\n"
              "Shoutout to Nguoilbianhz | Bot hoạt động 24/7"
          ),
          color=discord.Color.blue(),
      )
      await interaction.edit_original_response(
          embed=embed, view=MainCategoryView()
      )

    back_btn.callback = back_callback
    self.add_item(back_btn)


class BypassButton(discord.ui.Button):

  def __init__(self, label: str, style: discord.ButtonStyle, emoji: str):
    super().__init__(label=label, style=style, emoji=emoji)

  async def callback(self, interaction: discord.Interaction):
    modal = BypassModal(platform_name=self.label)
    await interaction.response.send_modal(modal)


# ================= GIAO DIỆN CẤP 1: CHỌN KHU VỰC =================
class MainCategoryView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=60)

  @discord.ui.button(
      label="Nền tảng Việt Nam", style=discord.ButtonStyle.primary, emoji="🇻🇳"
  )
  async def vn_btn(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        title="🇻🇳 Nền tảng Việt Nam",
        description="Chọn dịch vụ rút gọn / traffic bên dưới:",
        color=discord.Color.green(),
    )
    await interaction.edit_original_response(
        embed=embed, view=SubPlatformView("vn")
    )

  @discord.ui.button(
      label="Nền tảng Quốc tế", style=discord.ButtonStyle.success, emoji="🌍"
  )
  async def global_btn(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        title="🌍 Nền tảng Quốc tế",
        description="Chọn dịch vụ quốc tế bên dưới:",
        color=discord.Color.orange(),
    )
    await interaction.edit_original_response(
        embed=embed, view=SubPlatformView("global")
    )


# ================= LỆNH SLASH =================
@bot.tree.command(
    name="bypass", description="Mở menu chọn khu vực và hệ thống bypass"
)
async def bypass_command(interaction: discord.Interaction) -> None:
  embed = discord.Embed(
      title="⚙️ Hệ thống Bypass Tự động",
      description=(
          "Vui lòng chọn khu vực nền tảng bạn muốn vượt link ở bên dưới:\n"
          "Shoutout to Nguoilbianhz | Bot hoạt động 24/7"
      ),
      color=discord.Color.blue(),
  )
  await interaction.response.send_message(
      embed=embed, view=MainCategoryView(), ephemeral=True
  )


def main() -> None:
  if not DISCORD_TOKEN:
    raise SystemExit("Missing DISCORD_TOKEN")
  keep_alive()
  bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
  main()
