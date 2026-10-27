import discord
from discord import app_commands
from groq import Groq
from threading import Thread
from flask import Flask
import os
import asyncio

app = Flask('')

@app.route('/')
def home():
    return "New Alliance Translator is Online 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# Nayi Groq API Key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or ("gsk_gx8xW8O6ViUhH8RO74m" + "DWGdyb3FYGCIXJbNNPUlXEFfKWFBg8boL")
# Naya Discord Token
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN") or ("MTU2NDYxNzk4OTExMjczMzg2Nw" + ".G97iiO." + "GTTQDDI14SoUbJSdsOPSNgvY8xzRWQGX3_C9IA")

groq_client = Groq(api_key=GROQ_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

FLAG_MAP = {
    "🇮🇳": "Hinglish (Natural Indian Hindi written in Roman/Latin alphabet)",
    "🇯🇵": "Japanese",
    "🇮🇩": "Indonesian",
    "🇺🇸": "English",
    "🇬🇧": "English",
    "🇰🇷": "Korean",
    "🇻🇳": "Vietnamese",
    "🇷🇺": "Russian",
    "🇹🇭": "Thai",
    "🇵🇭": "Filipino (Tagalog)",
    "🇪🇸": "Spanish",
    "🇧🇷": "Portuguese",
    "🇹🇷": "Turkish",
    "🇸🇦": "Arabic",
    "🇩🇪": "German",
    "🇫🇷": "French",
    "🇨🇳": "Simplified Chinese",
    "🇹🇼": "Traditional Chinese"
}

def translate_text(text, target_lang):
    system_prompt = (
        f"You are an expert gaming translator for an international war-game Discord server. "
        f"Auto-detect the source language of the user's message and translate it accurately into {target_lang}.\n"
        f"Rules:\n"
        f"1. Understand local slang, idioms, gaming terms (castle, rally, NAP, mine, crystal, shield, tile hit, garrison, alliance).\n"
        f"2. If target is Hinglish, write ONLY in Roman/Latin script in natural Indian gamer tone.\n"
        f"3. Output ONLY the final translated text without any explanations."
    )
    try:
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=3000,
            timeout=15.0
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Translation error: {e}"

async def send_long_message(interaction, text):
    chunks = [text[i:i+1990] for i in range(0, len(text), 1990)]
    for chunk in chunks:
        await interaction.followup.send(chunk, ephemeral=True)

async def handle_private_translation(interaction: discord.Interaction, message: discord.Message, target_lang: str, label: str):
    if not message.content:
        await interaction.response.send_message("Is message mein translate karne ke liye koi text nahi hai.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    translated = await asyncio.to_thread(translate_text, message.content, target_lang)
    final_output = f"**[Reply to {message.author.display_name}]:**\n{translated}"
    await send_long_message(interaction, final_output)

@tree.context_menu(name="🇮🇳 Translate to Hinglish")
async def tr_hinglish(interaction: discord.Interaction, message: discord.Message):
    await handle_private_translation(interaction, message, FLAG_MAP["🇮🇳"], "🇮🇳 Hinglish")

@tree.context_menu(name="🇯🇵 Translate to Japanese")
async def tr_japanese(interaction: discord.Interaction, message: discord.Message):
    await handle_private_translation(interaction, message, "Japanese", "🇯🇵 Japanese")

@tree.context_menu(name="🇮🇩 Translate to Indonesian")
async def tr_indonesian(interaction: discord.Interaction, message: discord.Message):
    await handle_private_translation(interaction, message, "Indonesian", "🇮🇩 Indonesian")

@tree.context_menu(name="🇺🇸 Translate to English")
async def tr_english(interaction: discord.Interaction, message: discord.Message):
    await handle_private_translation(interaction, message, "English", "🇺🇸 English")

class LanguageDropdown(discord.ui.Select):
    def __init__(self, target_message: discord.Message):
        self.target_message = target_message
        options = [
            discord.SelectOption(label="Hinglish (India)", emoji="🇮🇳", value="Hinglish (Natural Indian Hindi in Roman script)"),
            discord.SelectOption(label="Japanese", emoji="🇯🇵", value="Japanese"),
            discord.SelectOption(label="Indonesian", emoji="🇮🇩", value="Indonesian"),
            discord.SelectOption(label="English", emoji="🇺🇸", value="English"),
            discord.SelectOption(label="Korean", emoji="🇰🇷", value="Korean"),
            discord.SelectOption(label="Vietnamese", emoji="🇻🇳", value="Vietnamese"),
            discord.SelectOption(label="Russian", emoji="🇷🇺", value="Russian"),
            discord.SelectOption(label="Thai", emoji="🇹🇭", value="Thai"),
            discord.SelectOption(label="Filipino", emoji="🇵🇭", value="Filipino (Tagalog)"),
            discord.SelectOption(label="Arabic", emoji="🇸🇦", value="Arabic"),
            discord.SelectOption(label="Spanish", emoji="🇪🇸", value="Spanish"),
            discord.SelectOption(label="Portuguese", emoji="🇧🇷", value="Portuguese"),
            discord.SelectOption(label="Turkish", emoji="🇹🇷", value="Turkish"),
            discord.SelectOption(label="German", emoji="🇩🇪", value="German"),
            discord.SelectOption(label="French", emoji="🇫🇷", value="French"),
            discord.SelectOption(label="Chinese", emoji="🇨🇳", value="Simplified Chinese")
        ]
        super().__init__(placeholder="Choose your language...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        chosen_lang = self.values[0]
        translated = await asyncio.to_thread(translate_text, self.target_message.content, chosen_lang)
        final_output = f"**[Reply to {self.target_message.author.display_name}]:**\n{translated}"
        chunks = [final_output[i:i+1990] for i in range(0, len(final_output), 1990)]
        for chunk in chunks:
            await interaction.followup.send(chunk, ephemeral=True)

class LanguageView(discord.ui.View):
    def __init__(self, target_message: discord.Message):
        super().__init__(timeout=60)
        self.add_item(LanguageDropdown(target_message))

@tree.context_menu(name="🌍 Other Languages (Translate)")
async def tr_other(interaction: discord.Interaction, message: discord.Message):
    if not message.content:
        await interaction.response.send_message("No text found in this message.", ephemeral=True)
        return
    await interaction.response.send_message("Select your language below:", view=LanguageView(message), ephemeral=True)

@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

@client.event
async def on_raw_reaction_add(payload):
    if payload.user_id == client.user.id:
        return
    emoji = str(payload.emoji)
    if emoji in FLAG_MAP:
        channel = client.get_channel(payload.channel_id)
        if not channel:
            return
        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception:
            return
        if not message.content:
            return
        user = await client.fetch_user(payload.user_id)
        if user:
            target_lang = FLAG_MAP[emoji]
            translated = await asyncio.to_thread(translate_text, message.content, target_lang)
            final_output = f"**[Reply to {message.author.display_name}]:**\n{translated}"
            try:
                chunks = [final_output[i:i+1990] for i in range(0, len(final_output), 1990)]
                for chunk in chunks:
                    await user.send(chunk)
            except discord.Forbidden:
                pass

keep_alive()
client.run(DISCORD_TOKEN)
      
