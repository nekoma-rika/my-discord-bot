import discord
from discord import app_commands
from discord.ext import commands
import asyncio

# --- 1. タイトル変更用モーダル ---
class RenameModal(discord.ui.Modal, title='タイトル変更'):
    new_name = discord.ui.TextInput(label='新しい名前')
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.channel.edit(name=str(self.new_name))
        await interaction.response.send_message("変更できたよ！", ephemeral=True)

# --- 2. 削除確認用ビュー ---
class DeleteConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=10)
    @discord.ui.button(label="本当に削除する", style=discord.ButtonStyle.danger)
    async def confirm_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if isinstance(interaction.channel, discord.Thread):
            await interaction.channel.delete()

# --- 3. スレッド管理用ビュー ---
class ThreadManageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="タイトル変更", style=discord.ButtonStyle.primary, custom_id="rename_btn")
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RenameModal())
    @discord.ui.button(label="スレッドを閉じる（クローズ+ロック）", style=discord.ButtonStyle.danger, custom_id="lock_btn")
    async def lock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("スレッドを閉じたよ！", ephemeral=True)
        await interaction.channel.edit(archived=True, locked=True)
    @discord.ui.button(label="スレッドを削除", style=discord.ButtonStyle.secondary, custom_id="delete_btn")
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("本当に削除しちゃう…？", view=DeleteConfirmView(), ephemeral=True)

# --- 4. スレッド作成用モーダル ---
class CreateThreadModal(discord.ui.Modal, title='プライベートスレッドを作成'):
    name = discord.ui.TextInput(label='スレッド名')
    async def on_submit(self, interaction: discord.Interaction):
        user_mention = interaction.user.mention
        # プライベートスレッドを作成
        thread = await interaction.channel.create_thread(
            name=str(self.name),
            type=discord.ChannelType.private_thread
        )
        await thread.send(f"{user_mention} 準備ができたよ！", view=ThreadManageView())
        await interaction.response.send_message(f"作れたよ！\n{thread.mention}", ephemeral=True)

# --- 5. 設置用ビュー ---
class SetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="プライベートスレッドを作成", style=discord.ButtonStyle.success, custom_id="create_btn")
    async def create_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CreateThreadModal())

# --- 6. Cog本体 ---
class ThreadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup", description="作成ボタンを設置")
    async def setup(self, interaction: discord.Interaction):
        # 変数 desc に内容をまとめる
        desc = (
            "このチャンネルでプライベートスレッドを作成できるよ！\n\n"
            "### 作成方法\n"
            "下にあるスレッド作成ボタンを押して、タイトルを入力すれば作れるよ！\n\n"
            "### 終了方法\n"
            "「スレッドを閉じる」ボタンを押せばクローズとロックがされるよ！\n"
            "-# ⚠️ ボツになったのは削除ボタンで消してね！\n\n"
            "### 招待方法\n"
            "メンション（@ユーザー名）を送れば招待できるよ！"
        )

        # Embedの作成
        embed = discord.Embed(
            title="プライベートスレッド作成",
            description=desc,
            color=discord.Color.blue()
        )

        await interaction.channel.send(embed=embed, view=SetupView())
        await interaction.response.send_message("パネルを置いたよ！", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ThreadCog(bot))