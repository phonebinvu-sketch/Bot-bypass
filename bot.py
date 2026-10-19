import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Tải biến môi trường từ file .env cục bộ
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Cấu hình Intents cho Bot
intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)
tree = client.tree

# Danh sách các trang hỗ trợ hiển thị trong /helpbypass
SUPPORTED_PLATFORMS = {
    "🇻🇳 Nền tảng Việt Nam": ["L4M", "Phienchoso", "Sitetop", "BBMKTS", "Gtraffic", "Site2s"],
    "🌍 Nền tảng Quốc tế": ["Delta", "Linkvertise", "Lootlabs", "Work.ink"]
}

@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot Bypass đã hoạt động thành công với tên: {client.user}")

# ================= 1. GIAO DIỆN MODAL (NHẬP LINK) =================
class BypassModal(discord.ui.Modal):
    def __init__(self, platform_name: str):
        super().__init__(title=f"Bypass Link - {platform_name}")
        self.platform_name = platform_name

        # Ô nhập link
        self.link_input = discord.ui.TextInput(
            label="Dán đường dẫn cần bypass vào đây",
            placeholder="Ví dụ: https://...",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.link_input)

    async def on_submit(self, interaction: discord.Interaction):
        # Phản hồi ẩn (chỉ người dùng thấy)
        await interaction.response.defer(ephemeral=True)
        
        user_link = self.link_input.value

        try:
            # ===== ĐOẠN CODE GỌI LOGIC BYPASS THỰC TẾ CỦA BẠN Ở ĐÂY =====
            bypassed_result = (
                f"🔓 **Bypass thành công!**\n"
                f"📌 **Hệ thống:** `{self.platform_name}`\n"
                f"🔑 **Kết quả (Key/Link):** `SAMPLE-KEY-XYZ-12345`\n"
                f"🌐 **Link gốc:** {user_link}"
            )
            # ==========================================================

            await interaction.followup.send(bypassed_result, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"❌ Có lỗi xảy ra khi xử lý: {str(e)}", ephemeral=True)


# ================= 2. GIAO DIỆN NÚT BẤM (BUTTONS) =================
class PlatformSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    async def handle_click(self, interaction: discord.Interaction, platform_name: str):
        modal = BypassModal(platform_name=platform_name)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="L4M", style=discord.ButtonStyle.primary, emoji="🔗")
    async def l4m_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "L4M")

    @discord.ui.button(label="Delta", style=discord.ButtonStyle.success, emoji="⚡")
    async def delta_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Delta")

    @discord.ui.button(label="Work.ink", style=discord.ButtonStyle.danger, emoji="🌐")
    async def workink_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Work.ink")

    @discord.ui.button(label="Linkvertise", style=discord.ButtonStyle.secondary, emoji="🛡️")
    async def linkvertise_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Linkvertise")

    @discord.ui.button(label="Trang Khác (VN)", style=discord.ButtonStyle.primary, emoji="📌")
    async def others_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Phienchoso / Sitetop / BBMKTS / Gtraffic / Site2s")


# ================= 3. ĐỊNH NGHĨA CÁC LỆNH SLASH =================

@tree.command(name="bypass", description="Mở menu chọn hệ thống để vượt link và lấy key")
async def bypass(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚙️ Hệ thống Bypass Tự động",
        description="Chọn nền tảng/hệ thống bạn muốn vượt link ở danh sách bên dưới:",
        color=discord.Color.green()
    )
    embed.set_footer(text="Được vận hành bởi NoAdsM+ Bot")
    
    view = PlatformSelectView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


@tree.command(name="helpbypass", description="Xem danh sách các trang web được bot hỗ trợ bypass")
async def helpbypass(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📚 Danh sách trang web hỗ trợ Bypass",
        description="Dưới đây là các nền tảng rút gọn và vượt link hiện đang được tích hợp:",
        color=discord.Color.blue()
    )

    for category, platforms in SUPPORTED_PLATFORMS.items():
        embed.add_field(name=category, value=", ".join([f"`{p}`" for p in platforms]), inline=False)

    embed.set_footer(text="Gõ lệnh /bypass để bắt đầu sử dụng.")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Khởi chạy bot thông qua biến an toàn trong file .env
client.run(TOKEN)