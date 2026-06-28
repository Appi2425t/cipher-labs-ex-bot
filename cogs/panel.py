import discord
from discord.ext import commands
from discord import ui
import json
from utils import has_admin_role, CATEGORY_INFO


# --- Modals ---

class I2CModal(ui.Modal, title="💸 INR → Crypto Exchange"):
    amount = ui.TextInput(label="Amount (INR)", placeholder="e.g. 5000", required=True)
    crypto_type = ui.TextInput(label="Crypto Type", placeholder="USDT / SOL / LTC / BTC", required=True)
    payment_app = ui.TextInput(label="Payment App", placeholder="MBK / GPay / PhonePe", required=True)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        modal_answers = {
            "Amount (INR)": self.amount.value,
            "Crypto Type": self.crypto_type.value,
            "Payment App": self.payment_app.value,
        }
        from cogs.tickets import open_ticket
        await open_ticket(self.bot, interaction, "i2c", modal_answers)


class C2IModal(ui.Modal, title="💰 Crypto → INR Exchange"):
    amount = ui.TextInput(label="Amount (USD $)", placeholder="e.g. 50", required=True)
    crypto_type = ui.TextInput(label="Crypto Type", placeholder="USDT / SOL / LTC / BTC", required=True)
    wallet = ui.TextInput(label="Your Wallet", placeholder="CWallet / TrustWallet / Other", required=True)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        modal_answers = {
            "Amount (USD $)": self.amount.value,
            "Crypto Type": self.crypto_type.value,
            "Wallet": self.wallet.value,
        }
        from cogs.tickets import open_ticket
        await open_ticket(self.bot, interaction, "c2i", modal_answers)


class C2CModal(ui.Modal, title="🔄 Crypto → Crypto Exchange"):
    amount = ui.TextInput(label="Amount Sending (USD $)", placeholder="e.g. 100", required=True)
    crypto_sending = ui.TextInput(label="Crypto Sending", placeholder="e.g. USDT", required=True)
    crypto_receiving = ui.TextInput(label="Crypto Receiving", placeholder="e.g. SOL", required=True)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        modal_answers = {
            "Amount Sending (USD $)": self.amount.value,
            "Crypto Sending": self.crypto_sending.value,
            "Crypto Receiving": self.crypto_receiving.value,
        }
        from cogs.tickets import open_ticket
        await open_ticket(self.bot, interaction, "c2c", modal_answers)


class SupportModal(ui.Modal, title="🎧 Support"):
    issue = ui.TextInput(label="Describe your issue", style=discord.TextStyle.paragraph, placeholder="Explain your issue in detail...", required=True)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        modal_answers = {
            "Issue": self.issue.value,
        }
        from cogs.tickets import open_ticket
        await open_ticket(self.bot, interaction, "support", modal_answers)


class DisputeModal(ui.Modal, title="⚠️ Dispute / Issue"):
    reference = ui.TextInput(label="Ticket Reference (optional)", required=False, placeholder="e.g. #0042")
    dispute = ui.TextInput(label="Describe the dispute", style=discord.TextStyle.paragraph, placeholder="Explain the dispute in detail...", required=True)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        modal_answers = {
            "Ticket Reference": self.reference.value or "N/A",
            "Dispute": self.dispute.value,
        }
        from cogs.tickets import open_ticket
        await open_ticket(self.bot, interaction, "dispute", modal_answers)


# --- Panel Views ---

class ExchangePanelView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(ExchangeSelect(bot))


class ExchangeSelect(ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="INR 2 Crypto", value="i2c", emoji="💸", description="Pay with INR, receive crypto"),
            discord.SelectOption(label="Crypto 2 INR", value="c2i", emoji="💰", description="Send crypto, receive INR"),
            discord.SelectOption(label="Crypto 2 Crypto", value="c2c", emoji="🔄", description="Swap one crypto for another"),
        ]
        super().__init__(placeholder="Select exchange type to open a ticket...", options=options, custom_id="panel:exchange_select")

    async def callback(self, interaction: discord.Interaction):
        value = self.values[0]
        if value == "i2c":
            await interaction.response.send_modal(I2CModal(self.bot))
        elif value == "c2i":
            await interaction.response.send_modal(C2IModal(self.bot))
        elif value == "c2c":
            await interaction.response.send_modal(C2CModal(self.bot))


class SupportPanelView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(SupportSelect(bot))


class SupportSelect(ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Support", value="support", emoji="🎧"),
            discord.SelectOption(label="Dispute / Issue", value="dispute", emoji="⚠️"),
        ]
        super().__init__(placeholder="Select support type...", options=options, custom_id="panel:support_select")

    async def callback(self, interaction: discord.Interaction):
        value = self.values[0]
        if value == "support":
            await interaction.response.send_modal(SupportModal(self.bot))
        elif value == "dispute":
            await interaction.response.send_modal(DisputeModal(self.bot))


# --- Panel Creation Modals ---

class CreateExchangePanelModal(ui.Modal, title="Create Exchange Panel"):
    panel_title = ui.TextInput(label="Panel Title", default="🌸 CIPHER LABS 🌸", required=True)
    description = ui.TextInput(
        label="Description",
        style=discord.TextStyle.paragraph,
        default="₹ **INR 2 CRYPTO**\n> 103.0/$ Any Amount\n\n🪙 **CRYPTO 2 INR**\n> 99/$ for Below $100\n> 100/$ for Above $100\n\n🪙 **CRYPTO 2 CRYPTO**\n> 3.0% fee + transaction fees\n\nRead our rules before proceeding.\nFixed rates. No negotiations.\n\n**TRUSTED & SAFE SERVICE**",
        required=True
    )
    color = ui.TextInput(label="Color (hex)", default="#f1c40f", required=False)
    footer = ui.TextInput(label="Footer Text", default="Cipher Labs • Trusted Exchange", required=False)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        from utils import hex_to_int
        color_val = hex_to_int(self.color.value) if self.color.value else 3447003
        embed = discord.Embed(
            title=self.panel_title.value,
            description=self.description.value,
            color=color_val
        )
        if self.footer.value:
            embed.set_footer(text=self.footer.value)

        view = ExchangePanelView(self.bot)
        msg = await interaction.channel.send(embed=embed, view=view)

        await self.bot.db.create_panel(
            interaction.guild_id, interaction.channel_id, msg.id,
            self.panel_title.value, self.description.value, color_val,
            self.footer.value, None, "exchange"
        )
        await interaction.response.send_message("✅ Exchange panel created!", ephemeral=True)


class CreateSupportPanelModal(ui.Modal, title="Create Support Panel"):
    panel_title = ui.TextInput(label="Panel Title", default="🎧 Support & Disputes", required=True)
    description = ui.TextInput(label="Description", style=discord.TextStyle.paragraph, default="Need help? Select an option below.", required=True)
    color = ui.TextInput(label="Color (hex)", default="#e74c3c", required=False)
    footer = ui.TextInput(label="Footer Text", default="Cipher Labs • Support", required=False)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        from utils import hex_to_int
        color_val = hex_to_int(self.color.value) if self.color.value else 3447003
        embed = discord.Embed(
            title=self.panel_title.value,
            description=self.description.value,
            color=color_val
        )
        if self.footer.value:
            embed.set_footer(text=self.footer.value)

        view = SupportPanelView(self.bot)
        msg = await interaction.channel.send(embed=embed, view=view)

        await self.bot.db.create_panel(
            interaction.guild_id, interaction.channel_id, msg.id,
            self.panel_title.value, self.description.value, color_val,
            self.footer.value, None, "support"
        )
        await interaction.response.send_message("✅ Support panel created!", ephemeral=True)


# --- Panel Cog ---

class PanelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ExchangePanelView(self.bot))
        self.bot.add_view(SupportPanelView(self.bot))

    @commands.group(name="panel", invoke_without_command=True)
    async def panel(self, ctx: commands.Context):
        await ctx.send("Usage: `.panel create-exchange`, `.panel create-support`, `.panel list`, `.panel delete <id>`, `.panel send <id> #channel`")

    @panel.command(name="create-exchange")
    async def create_exchange(self, ctx: commands.Context):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        await ctx.send("Opening panel creation modal... Please use the button below.", view=CreateExchangeButtonView(self.bot))

    @panel.command(name="exchange")
    async def quick_exchange(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """Quickly post the exchange panel with rates to a channel."""
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return

        target = channel or ctx.channel
        rate_i2c = config.get("rate_i2c") or 101
        rate_c2i_below = config.get("rate_c2i_below") or 97.5
        rate_c2i_above = config.get("rate_c2i_above") or 98.5
        rate_c2c = config.get("rate_c2c") or 100
        c2c_fee = round(100 - rate_c2c, 1)

        description = (
            f"₹ **INR 2 CRYPTO**\n"
            f"> {rate_i2c}/$ Any Amount\n\n"
            f"🪙 **CRYPTO 2 INR**\n"
            f"> {rate_c2i_below}/$ for Below $100\n"
            f"> {rate_c2i_above}/$ for Above $100\n\n"
            f"🪙 **CRYPTO 2 CRYPTO**\n"
            f"> {c2c_fee}% fee + transaction fees\n\n"
            f"Read our rules before proceeding.\n"
            f"Fixed rates. No negotiations.\n\n"
            f"**TRUSTED & SAFE SERVICE**"
        )

        embed = discord.Embed(
            title="🌸 CIPHER LABS 🌸",
            description=description,
            color=0xf1c40f
        )
        embed.set_footer(text="Cipher Labs • Trusted Exchange")

        view = ExchangePanelView(self.bot)
        msg = await target.send(embed=embed, view=view)

        await self.bot.db.create_panel(
            ctx.guild.id, target.id, msg.id,
            "🌸 CIPHER LABS 🌸", description, 0xf1c40f,
            "Cipher Labs • Trusted Exchange", None, "exchange"
        )
        if target != ctx.channel:
            await ctx.send(f"✅ Exchange panel posted in {target.mention}")
        else:
            await ctx.message.delete()

    @panel.command(name="create-support")
    async def create_support(self, ctx: commands.Context):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        await ctx.send("Opening panel creation modal... Please use the button below.", view=CreateSupportButtonView(self.bot))

    @panel.command(name="list")
    async def panel_list(self, ctx: commands.Context):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        panels = await self.bot.db.get_panels(ctx.guild.id)
        if not panels:
            await ctx.send("No panels found.")
            return
        desc = ""
        for p in panels:
            desc += f"**ID {p['id']}** — {p['panel_type']} in <#{p['channel_id']}>\n"
        embed = discord.Embed(title="📋 Panels", description=desc, color=discord.Color.blue())
        await ctx.send(embed=embed)

    @panel.command(name="delete")
    async def panel_delete(self, ctx: commands.Context, panel_id: int):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        panel = await self.bot.db.get_panel(panel_id)
        if not panel or panel["guild_id"] != ctx.guild.id:
            await ctx.send("❌ Panel not found.")
            return
        # Try to delete the message
        try:
            channel = ctx.guild.get_channel(panel["channel_id"])
            if channel:
                msg = await channel.fetch_message(panel["message_id"])
                await msg.delete()
        except Exception:
            pass
        await self.bot.db.delete_panel(panel_id)
        await ctx.send(f"✅ Panel #{panel_id} deleted.")

    @panel.command(name="send")
    async def panel_send(self, ctx: commands.Context, panel_id: int, channel: discord.TextChannel):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        panel = await self.bot.db.get_panel(panel_id)
        if not panel or panel["guild_id"] != ctx.guild.id:
            await ctx.send("❌ Panel not found.")
            return

        embed = discord.Embed(
            title=panel["title"] or "Panel",
            description=panel["description"] or "",
            color=panel["color"] or 3447003
        )
        if panel["footer"]:
            embed.set_footer(text=panel["footer"])

        if panel["panel_type"] == "exchange":
            view = ExchangePanelView(self.bot)
        else:
            view = SupportPanelView(self.bot)

        msg = await channel.send(embed=embed, view=view)
        # Update panel record with new message/channel
        await self.bot.db.create_panel(
            ctx.guild.id, channel.id, msg.id,
            panel["title"], panel["description"], panel["color"],
            panel["footer"], panel["thumbnail"], panel["panel_type"]
        )
        await ctx.send(f"✅ Panel sent to {channel.mention}")

    @panel.command(name="edit")
    async def panel_edit(self, ctx: commands.Context, panel_id: int):
        """Edit an existing panel. Usage: .panel edit <id>"""
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        panel = await self.bot.db.get_panel(panel_id)
        if not panel or panel["guild_id"] != ctx.guild.id:
            await ctx.send("❌ Panel not found.")
            return
        await ctx.send(
            f"Editing panel **#{panel_id}** ({panel['panel_type']}). Click below to open the editor.",
            view=EditPanelButtonView(self.bot, panel)
        )


class CreateExchangeButtonView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=60)
        self.bot = bot

    @ui.button(label="Create Exchange Panel", style=discord.ButtonStyle.green)
    async def create_btn(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(CreateExchangePanelModal(self.bot))


class CreateSupportButtonView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=60)
        self.bot = bot

    @ui.button(label="Create Support Panel", style=discord.ButtonStyle.green)
    async def create_btn(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(CreateSupportPanelModal(self.bot))


class EditPanelButtonView(ui.View):
    def __init__(self, bot, panel):
        super().__init__(timeout=60)
        self.bot = bot
        self.panel = panel

    @ui.button(label="Edit Panel", style=discord.ButtonStyle.blurple, emoji="✏️")
    async def edit_btn(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(EditPanelModal(self.bot, self.panel))


class EditPanelModal(ui.Modal, title="✏️ Edit Panel"):
    def __init__(self, bot, panel):
        super().__init__()
        self.bot = bot
        self.panel = panel
        self.panel_title_input = ui.TextInput(
            label="Panel Title",
            default=panel.get("title") or "",
            required=True
        )
        self.description_input = ui.TextInput(
            label="Description",
            style=discord.TextStyle.paragraph,
            default=panel.get("description") or "",
            required=True
        )
        self.color_input = ui.TextInput(
            label="Color (hex)",
            default=f"#{panel.get('color', 3447003):06x}",
            required=False
        )
        self.footer_input = ui.TextInput(
            label="Footer Text",
            default=panel.get("footer") or "",
            required=False
        )
        self.add_item(self.panel_title_input)
        self.add_item(self.description_input)
        self.add_item(self.color_input)
        self.add_item(self.footer_input)

    async def on_submit(self, interaction: discord.Interaction):
        from utils import hex_to_int
        new_title = self.panel_title_input.value
        new_desc = self.description_input.value
        new_color = hex_to_int(self.color_input.value) if self.color_input.value else self.panel.get("color", 3447003)
        new_footer = self.footer_input.value

        # Update the panel message
        try:
            channel = interaction.guild.get_channel(self.panel["channel_id"])
            if channel:
                msg = await channel.fetch_message(self.panel["message_id"])
                embed = discord.Embed(
                    title=new_title,
                    description=new_desc,
                    color=new_color
                )
                if new_footer:
                    embed.set_footer(text=new_footer)
                await msg.edit(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Could not edit the message: {e}", ephemeral=True)
            return

        # Update DB
        await self.bot.db.update_panel(
            self.panel["id"],
            title=new_title,
            description=new_desc,
            color=new_color,
            footer=new_footer
        )
        await interaction.response.send_message("✅ Panel updated successfully!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(PanelCog(bot))
