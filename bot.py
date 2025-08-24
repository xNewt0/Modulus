import requests
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import re
import random
from datetime import datetime, timedelta, timezone
import sqlite3
from sqlite3 import Error
import math
import time
import os
import requests.exceptions
import colorama
from colorama import Fore, Style
import pyfiglet

# Colorama'yı başlat
colorama.init()

# ASCII başlık oluştur
print("\033[36m")  # camgöbeği başlat
print(r"""
   ▄▄▄▄███▄▄▄▄    ▄██████▄  ████████▄  ███    █▄   ▄█       ███    █▄ 
 ▄██▀▀▀███▀▀▀██▄ ███    ███ ███   ▀███ ███    ███ ███       ███    ███
 ███   ███   ███ ███    ███ ███    ███ ███    ███ ███       ███    ███
 ███   ███   ███ ███    ███ ███    ███ ███    ███ ███       ███    ███
 ███   ███   ███ ███    ███ ███    ███ ███    ███ ███       ███    ███
 ███   ███   ███ ███    ███ ███    ███ ███    ███ ███       ███    ███
 ███   ███   ███ ███    ███ ███   ▄███ ███    ███ ███▌    ▄ ███    ███
  ▀█   ███   █▀   ▀██████▀  ████████▀  ████████▀  █████▄▄██ ████████▀ 
                                                  ▀                   
   ▄████████                                                          
  ███    ███                                                          
  ███    █▀                                                           
  ███                                                                 
▀███████████                                                          
         ███                                                          
   ▄█    ███                                                          
 ▄████████▀                                                           
""")
print("\033[0m")  


# Token alma
token = input(Fore.GREEN + "Bot tokeninizi giriniz: " + Style.RESET_ALL)
# Owner ID'leri alma
owner_input = input(Fore.GREEN + "Owner ID giriniz birden fazla olacak ise virgülle ayırabilirsiniz.: " + Style.RESET_ALL)
OWNER_IDS = [int(x.strip()) for x in owner_input.split(",") if x.strip().isdigit()]

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


# Çift loglamayı önlemek için global set
deleted_messages = set()

@bot.check
async def global_owner_check(ctx):
    return ctx.author.id in OWNER_IDS

# --- SQL Veritabanı Ayarları ---
def create_connection():
    try:
        return sqlite3.connect('newtDATA.db')
    except Error as e:
        print(f"{Fore.RED}Veritabanı bağlantı hatası: {e}{Style.RESET_ALL}")
    return None

def initialize_database():
    commands = [
        """CREATE TABLE IF NOT EXISTS warnings (
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            count INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (guild_id, user_id)
        );""",
        """CREATE TABLE IF NOT EXISTS log_channels (
            guild_id INTEGER PRIMARY KEY,
            channel_id INTEGER NOT NULL
        );""",
        """CREATE TABLE IF NOT EXISTS autoroles (
            guild_id INTEGER PRIMARY KEY,
            role_id INTEGER NOT NULL
        );""",
        """CREATE TABLE IF NOT EXISTS immune_users (
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY (guild_id, user_id)
        );""",
        """CREATE TABLE IF NOT EXISTS suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            suggestion TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );""",
        """CREATE TABLE IF NOT EXISTS mod_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            moderator_id INTEGER NOT NULL,
            reason TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );""",
        """CREATE TABLE IF NOT EXISTS level_config (
            guild_id INTEGER PRIMARY KEY,
            role1_id INTEGER,
            role2_id INTEGER,
            role3_id INTEGER,
            announcement_channels TEXT,
            log_channel_id INTEGER
        );""",
        """CREATE TABLE IF NOT EXISTS user_levels (
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            xp INTEGER NOT NULL DEFAULT 0,
            level INTEGER NOT NULL DEFAULT 0,
            last_message_time REAL,
            PRIMARY KEY (guild_id, user_id)
        );""",
        """CREATE TABLE IF NOT EXISTS language_roles (
            guild_id INTEGER PRIMARY KEY,
            role_tr INTEGER,
            role_en INTEGER,
            role_other INTEGER
        );""",
        """CREATE TABLE IF NOT EXISTS message_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            attachments TEXT,
            is_deleted BOOLEAN DEFAULT 0,
            is_edited BOOLEAN DEFAULT 0,
            moderator_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );""",
        """CREATE TABLE IF NOT EXISTS server_config (
            guild_id INTEGER PRIMARY KEY,
            setup_complete BOOLEAN DEFAULT 0
        );"""
    ]
    
    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            for command in commands:
                c.execute(command)
            conn.commit()
        except Error as e:
            print(f"{Fore.RED}Tablo oluşturma hatası: {e}{Style.RESET_ALL}")
        finally:
            conn.close()

# --- SQL Helper Functions ---
def get_warnings(guild_id: int, user_id: int) -> int:
    conn = create_connection()
    if not conn: return 0
    try:
        c = conn.cursor()
        c.execute("SELECT count FROM warnings WHERE guild_id=? AND user_id=?", (guild_id, user_id))
        result = c.fetchone()
        return result[0] if result else 0
    except Error as e:
        print(f"{Fore.RED}Uyarı getirme hatası: {e}{Style.RESET_ALL}")
        return 0
    finally:
        conn.close()

def add_warning(guild_id: int, user_id: int) -> int:
    conn = create_connection()
    if not conn: return 0
    try:
        c = conn.cursor()
        c.execute("SELECT count FROM warnings WHERE guild_id=? AND user_id=?", (guild_id, user_id))
        result = c.fetchone()
        new_count = result[0] + 1 if result else 1
        c.execute("""
            INSERT INTO warnings (guild_id, user_id, count) 
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, user_id) 
            DO UPDATE SET count = excluded.count
        """, (guild_id, user_id, new_count))
        conn.commit()
        return new_count
    except Error as e:
        print(f"{Fore.RED}Uyarı ekleme hatası: {e}{Style.RESET_ALL}")
        return 0
    finally:
        conn.close()

def remove_warning(guild_id: int, user_id: int) -> bool:
    conn = create_connection()
    if not conn: return False
    try:
        c = conn.cursor()
        c.execute("SELECT count FROM warnings WHERE guild_id=? AND user_id=?", (guild_id, user_id))
        result = c.fetchone()
        if not result: return False
        
        new_count = result[0] - 1
        if new_count <= 0:
            c.execute("DELETE FROM warnings WHERE guild_id=? AND user_id=?", (guild_id, user_id))
        else:
            c.execute("UPDATE warnings SET count=? WHERE guild_id=? AND user_id=?", (new_count, guild_id, user_id))
        conn.commit()
        return True
    except Error as e:
        print(f"{Fore.RED}Uyarı silme hatası: {e}{Style.RESET_ALL}")
        return False
    finally:
        conn.close()

def set_log_channel(guild_id: int, channel_id: int):
    conn = create_connection()
    if not conn: return
    try:
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO log_channels (guild_id, channel_id) 
            VALUES (?, ?)
        """, (guild_id, channel_id))
        conn.commit()
    except Error as e:
        print(f"{Fore.RED}Log kanalı ayarlama hatası: {e}{Style.RESET_ALL}")
    finally:
        conn.close()

def get_log_channel(guild_id: int) -> int:
    conn = create_connection()
    if not conn: return None
    try:
        c = conn.cursor()
        c.execute("SELECT channel_id FROM log_channels WHERE guild_id=?", (guild_id,))
        result = c.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"{Fore.RED}Log kanalı getirme hatası: {e}{Style.RESET_ALL}")
        return None
    finally:
        conn.close()

def set_autorole(guild_id: int, role_id: int):
    conn = create_connection()
    if not conn: return
    try:
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO autoroles (guild_id, role_id) 
            VALUES (?, ?)
        """, (guild_id, role_id))
        conn.commit()
    except Error as e:
        print(f"{Fore.RED}Otorol ayarlama hatası: {e}{Style.RESET_ALL}")
    finally:
        conn.close()

def get_autorole(guild_id: int) -> int:
    conn = create_connection()
    if not conn: return None
    try:
        c = conn.cursor()
        c.execute("SELECT role_id FROM autoroles WHERE guild_id=?", (guild_id,))
        result = c.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"{Fore.RED}Otorol getirme hatası: {e}{Style.RESET_ALL}")
        return None
    finally:
        conn.close()

def add_immune_user(guild_id: int, user_id: int):
    conn = create_connection()
    if not conn: return
    try:
        c = conn.cursor()
        c.execute("""
            INSERT OR IGNORE INTO immune_users (guild_id, user_id) 
            VALUES (?, ?)
        """, (guild_id, user_id))
        conn.commit()
    except Error as e:
        print(f"{Fore.RED}Immune kullanıcı ekleme hatası: {e}{Style.RESET_ALL}")
    finally:
        conn.close()

def remove_immune_user(guild_id: int, user_id: int) -> bool:
    conn = create_connection()
    if not conn: return False
    try:
        c = conn.cursor()
        c.execute("DELETE FROM immune_users WHERE guild_id=? AND user_id=?", (guild_id, user_id))
        conn.commit()
        return c.rowcount > 0
    except Error as e:
        print(f"{Fore.RED}Immune kullanıcı kaldırma hatası: {e}{Style.RESET_ALL}")
        return False
    finally:
        conn.close()

def is_immune(guild_id: int, user_id: int) -> bool:
    conn = create_connection()
    if not conn: return False
    try:
        c = conn.cursor()
        c.execute("SELECT 1 FROM immune_users WHERE guild_id=? AND user_id=?", (guild_id, user_id))
        return c.fetchone() is not None
    except Error as e:
        print(f"{Fore.RED}Immune kontrol hatası: {e}{Style.RESET_ALL}")
        return False
    finally:
        conn.close()

def add_suggestion(guild_id: int, user_id: int, suggestion: str) -> int:
    conn = create_connection()
    if not conn: return None
    try:
        c = conn.cursor()
        c.execute("""
            INSERT INTO suggestions (guild_id, user_id, suggestion) 
            VALUES (?, ?, ?)
        """, (guild_id, user_id, suggestion))
        conn.commit()
        return c.lastrowid
    except Error as e:
        print(f"{Fore.RED}Öneri ekleme hatası: {e}{Style.RESET_ALL}")
        return None
    finally:
        conn.close()

def get_suggestions(guild_id: int):
    conn = create_connection()
    if not conn: return []
    try:
        c = conn.cursor()
        c.execute("SELECT id, user_id, suggestion, timestamp FROM suggestions WHERE guild_id=?", (guild_id,))
        return c.fetchall()
    except Error as e:
        print(f"{Fore.RED}Önerileri getirme hatası: {e}{Style.RESET_ALL}")
        return []
    finally:
        conn.close()

def add_mod_history(guild_id: int, user_id: int, action: str, moderator_id: int, reason: str = None):
    conn = create_connection()
    if not conn: return
    try:
        c = conn.cursor()
        c.execute("""
            INSERT INTO mod_history (guild_id, user_id, action, moderator_id, reason) 
            VALUES (?, ?, ?, ?, ?)
        """, (guild_id, user_id, action, moderator_id, reason))
        conn.commit()
    except Error as e:
        print(f"{Fore.RED}Mod geçmişi ekleme hatası: {e}{Style.RESET_ALL}")
    finally:
        conn.close()

def get_mod_history(guild_id: int, user_id: int):
    conn = create_connection()
    if not conn: return []
    try:
        c = conn.cursor()
        c.execute("""
            SELECT action, reason, moderator_id, timestamp 
            FROM mod_history 
            WHERE guild_id=? AND user_id=?
        """, (guild_id, user_id))
        return c.fetchall()
    except Error as e:
        print(f"{Fore.RED}Mod geçmişi getirme hatası: {e}{Style.RESET_ALL}")
        return []
    finally:
        conn.close()

# --- Dil Rol Sistemi ---
def set_language_roles(guild_id: int, role_tr: int, role_en: int, role_other: int):
    conn = create_connection()
    if not conn: return
    try:
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO language_roles 
            (guild_id, role_tr, role_en, role_other) 
            VALUES (?, ?, ?, ?)
        """, (guild_id, role_tr, role_en, role_other))
        conn.commit()
    except Error as e:
        print(f"{Fore.RED}Dil rolleri ayarlama hatası: {e}{Style.RESET_ALL}")
    finally:
        conn.close()

def get_language_roles(guild_id: int):
    conn = create_connection()
    if not conn: return None
    try:
        c = conn.cursor()
        c.execute("""
            SELECT role_tr, role_en, role_other 
            FROM language_roles 
            WHERE guild_id=?
        """, (guild_id,))
        result = c.fetchone()
        if not result: return None
        return {
            "role_tr": result[0],
            "role_en": result[1],
            "role_other": result[2]
        }
    except Error as e:
        print(f"{Fore.RED}Dil rolleri getirme hatası: {e}{Style.RESET_ALL}")
        return None
    finally:
        conn.close()

# --- Level Sistemi SQL Fonksiyonları ---
def set_level_config(
    guild_id: int, 
    role1_id: int, 
    role2_id: int, 
    role3_id: int, 
    announcement_channel_ids: list, 
    log_channel_id: int
):
    conn = create_connection()
    if not conn: return
    try:
        channels_str = ",".join(str(ch_id) for ch_id in announcement_channel_ids) if announcement_channel_ids else ""
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO level_config 
            (guild_id, role1_id, role2_id, role3_id, announcement_channels, log_channel_id) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (guild_id, role1_id, role2_id, role3_id, channels_str, log_channel_id))
        conn.commit()
    except Error as e:
        print(f"{Fore.RED}Level konfig ayarlama hatası: {e}{Style.RESET_ALL}")
    finally:
        conn.close()

def get_level_config(guild_id: int):
    conn = create_connection()
    if not conn: return None
    try:
        c = conn.cursor()
        c.execute("""
            SELECT role1_id, role2_id, role3_id, announcement_channels, log_channel_id 
            FROM level_config 
            WHERE guild_id=?
        """, (guild_id,))
        result = c.fetchone()
        if not result: return None
        
        channels_str = result[3]
        channel_ids = [int(ch_id) for ch_id in channels_str.split(",")] if channels_str else []
        return {
            "role1_id": result[0],
            "role2_id": result[1],
            "role3_id": result[2],
            "announcement_channel_ids": channel_ids,
            "log_channel_id": result[4]
        }
    except Error as e:
        print(f"{Fore.RED}Level konfig getirme hatası: {e}{Style.RESET_ALL}")
        return None
    finally:
        conn.close()

def get_user_level(guild_id: int, user_id: int):
    conn = create_connection()
    if not conn: return (0, 0)
    try:
        c = conn.cursor()
        c.execute("""
            SELECT xp, level 
            FROM user_levels 
            WHERE guild_id=? AND user_id=?
        """, (guild_id, user_id))
        result = c.fetchone()
        return result if result else (0, 0)
    except Error as e:
        print(f"{Fore.RED}Kullanıcı level getirme hatası: {e}{Style.RESET_ALL}")
        return (0, 0)
    finally:
        conn.close()

def set_user_level(
    guild_id: int, 
    user_id: int, 
    xp: int, 
    level: int, 
    last_message_time: float = None
):
    conn = create_connection()
    if not conn: return
    try:
        c = conn.cursor()
        if last_message_time:
            c.execute("""
                INSERT OR REPLACE INTO user_levels 
                (guild_id, user_id, xp, level, last_message_time) 
                VALUES (?, ?, ?, ?, ?)
            """, (guild_id, user_id, xp, level, last_message_time))
        else:
            c.execute("""
                INSERT OR REPLACE INTO user_levels 
                (guild_id, user_id, xp, level) 
                VALUES (?, ?, ?, ?)
            """, (guild_id, user_id, xp, level))
        conn.commit()
    except Error as e:
        print(f"{Fore.RED}Kullanıcı level ayarlama hatası: {e}{Style.RESET_ALL}")
    finally:
        conn.close()

def update_user_xp(guild_id: int, user_id: int, xp_delta: int):
    conn = create_connection()
    if not conn: return (0, 0)
    try:
        c = conn.cursor()
        c.execute("""
            SELECT xp, level 
            FROM user_levels 
            WHERE guild_id=? AND user_id=?
        """, (guild_id, user_id))
        result = c.fetchone()
        
        current_xp = result[0] if result else 0
        current_level = result[1] if result else 0
        
        new_xp = max(0, current_xp + xp_delta)
        new_level = calculate_level(new_xp)
        
        set_user_level(guild_id, user_id, new_xp, new_level)
        return (new_xp, new_level)
    except Error as e:
        print(f"{Fore.RED}XP güncelleme hatası: {e}{Style.RESET_ALL}")
        return (0, 0)
    finally:
        conn.close()

# --- Mesaj Log Sistemi ---
def log_message(
    guild_id: int,
    channel_id: int,
    user_id: int,
    message_id: int,
    content: str,
    attachments: list = None,
    is_deleted: bool = False,
    is_edited: bool = False,
    moderator_id: int = None
):
    conn = create_connection()
    if not conn: return
    try:
        attachments_str = ",".join([a.url for a in attachments]) if attachments else ""
        c = conn.cursor()
        c.execute("""
            INSERT INTO message_logs (
                guild_id, channel_id, user_id, message_id, content, 
                attachments, is_deleted, is_edited, moderator_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            guild_id, channel_id, user_id, message_id, content,
            attachments_str, is_deleted, is_edited, moderator_id
        ))
        conn.commit()
    except Error as e:
        print(f"{Fore.RED}Mesaj loglama hatası: {e}{Style.RESET_ALL}")
    finally:
        conn.close()

def get_message_logs(guild_id: int, user_id: int = None, limit: int = 10):
    conn = create_connection()
    if not conn: return []
    try:
        c = conn.cursor()
        if user_id:
            c.execute("""
                SELECT * FROM message_logs 
                WHERE guild_id=? AND user_id=?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (guild_id, user_id, limit))
        else:
            c.execute("""
                SELECT * FROM message_logs 
                WHERE guild_id=?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (guild_id, limit))
        return c.fetchall()
    except Error as e:
        print(f"{Fore.RED}Mesaj logları getirme hatası: {e}{Style.RESET_ALL}")
        return []
    finally:
        conn.close()

# --- Level Sistemi Yardımcı Fonksiyonlar ---
def calculate_level(xp: int) -> int:
    level = 0
    while xp >= xp_for_level(level + 1):
        level += 1
    return level

def xp_for_level(level: int) -> int:
    return int(100 * (level ** 1.5))

# --- Global Variables ---
warn_limit = 3
mute_duration = timedelta(minutes=15)
XP_COOLDOWN = 1  # XP kazanma cooldown'u (saniye)
XP_PER_MESSAGE = 10  # Mesaj başına verilen XP
XP_PENALTY = 50  # Uyarı başına kaybedilen XP
LEVEL_ROLES = {1: "role1_id", 2: "role2_id", 3: "role3_id"}

# Küfür listesi
kufurler = [
    "salak", "aptal", "mal", "am", "amına", "sikiyim", "götünü", "gotunu",
    "annenin", "ananın", "oc", "oe", "ananı", "özürlü", "sik", "gavat",
    "orosbu", "evladı", "orospu", "oç", "mal", "a m k", "aq", "amk", "yarram",
    "yarrak", "mk", "ucube", "ifşa", "alınır", "dm", "satılır", "babanı",
    "karını", "bacını", "sürtük", "pic", "piç"
]

# Flood kontrol
user_messages = {}
@tree.command(name="soru", description="GPT-4 API ile etkileşim kurar")
async def soru(interaction: discord.Interaction, mesaj: str):
    # Mesaj uzunluğu kontrolü (Discord'un 2000 karakter sınırına göre)
    if len(mesaj) > 1500:
        await interaction.response.send_message(
            "❌ Soru çok uzun! Maksimum 1500 karakter kabul edebilirim.", 
            ephemeral=True
        )
        return
        
    await interaction.response.defer()
    
    try:
        api_url = f"https://suqul3162.vercel.app/api/gpt4?promt={mesaj}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code != 200:
            error_msg = f"⚠️ API hatası (Kod: {response.status_code})"
            await interaction.followup.send(error_msg)
            return
            
        cevap = response.text.strip()
        
        # Discord'un 2000 karakter sınırına uygun hale getirme
        if len(cevap) > 1950:
            cevap = cevap[:1950] + "\n[...] (devamı kısaltıldı)"
        
        # Formatlı yanıt
        await interaction.followup.send(
            f"**Soru:** {mesaj}\n\n"
            f"**Cevap:**\n{cevap}"
        )
        
    except requests.exceptions.Timeout:
        await interaction.followup.send("⏳ API yanıt vermedi. Lütfen daha sonra tekrar deneyin.")
    except requests.exceptions.RequestException as e:
        await interaction.followup.send(f"⚠️ Hata oluştu: {str(e)}")
        print(f"{Fore.RED}Soru komutu hatası: {e}{Style.RESET_ALL}")
       
    

# AFK Sistemi
afk_users = {}

@tree.command(name="sync")
async def sync(interaction: discord.Interaction):
    try:
        await tree.sync()
        await interaction.response.send_message("Komutlar senkronize edildi!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Senkronizasyon hatası: {e}", ephemeral=True)
        print(f"{Fore.RED}Senkronizasyon hatası: {e}{Style.RESET_ALL}")

# --- Dil Rol Sistemi Butonları ---
class LanguageSelect(discord.ui.View):
    def __init__(self, roles):
        super().__init__(timeout=None)
        self.roles = roles
        
    @discord.ui.button(label="Türkçe", style=discord.ButtonStyle.primary, custom_id="lang_tr")
    async def turkish_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.assign_role(interaction, self.roles["role_tr"])
        
    @discord.ui.button(label="English", style=discord.ButtonStyle.success, custom_id="lang_en")
    async def english_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.assign_role(interaction, self.roles["role_en"])
        
    @discord.ui.button(label="Diğer", style=discord.ButtonStyle.secondary, custom_id="lang_other")
    async def other_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.assign_role(interaction, self.roles["role_other"])
        
    async def assign_role(self, interaction: discord.Interaction, role_id: int):
        try:
            if not role_id:
                await interaction.response.send_message("Bu rol henüz ayarlanmamış!", ephemeral=True)
                return
                
            guild = interaction.guild
            role = guild.get_role(role_id)
            if not role:
                await interaction.response.send_message("Rol bulunamadı!", ephemeral=True)
                return
                
            # Mevcut dil rollerini kaldır
            lang_roles = get_language_roles(guild.id)
            if lang_roles:
                for r_id in lang_roles.values():
                    if r_id:
                        existing_role = guild.get_role(r_id)
                        if existing_role and existing_role in interaction.user.roles:
                            await interaction.user.remove_roles(existing_role)
            
            # Yeni rolü ekle
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f"Başarıyla {role.name} rolü verildi!", 
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"Rol atama hatası: {e}", ephemeral=True)
            print(f"{Fore.RED}Dil rolü atama hatası: {e}{Style.RESET_ALL}")

# --- Helper Functions ---
def embed_message(title: str, description: str, color=discord.Color.blue()):
    embed = discord.Embed(
        title=title, 
        description=description, 
        color=color,
        timestamp=datetime.now(timezone.utc)
    )
    return embed

async def log_gonder(guild_id: int, embed: discord.Embed):
    try:
        channel_id = get_log_channel(guild_id)
        if not channel_id: return
        
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)
    except Exception as e:
        print(f"{Fore.RED}Log gönderme hatası: {e}{Style.RESET_ALL}")

def parse_duration(sure: str) -> timedelta:
    pattern = r"(\d+)([smhdw])"
    match = re.fullmatch(pattern, sure.lower())
    if not match:
        raise ValueError("Geçersiz süre formatı. Örn: 10s, 1h, 1d, 1w")
    
    value, unit = match.groups()
    value = int(value)
    if unit == 's': return timedelta(seconds=value)
    elif unit == 'm': return timedelta(minutes=value)
    elif unit == 'h': return timedelta(hours=value)
    elif unit == 'd': return timedelta(days=value)
    elif unit == 'w': return timedelta(weeks=value)

def is_flood(guild_id: int, user_id: int, limit=5, period=10) -> bool:
    now = datetime.now(timezone.utc)
    
    # Kullanıcı mesaj geçmişini al veya oluştur
    if guild_id not in user_messages:
        user_messages[guild_id] = {}
    if user_id not in user_messages[guild_id]:
        user_messages[guild_id][user_id] = []
    
    # Eski mesajları temizle
    user_messages[guild_id][user_id] = [
        t for t in user_messages[guild_id][user_id] 
        if (now - t).total_seconds() <= period
    ]
    
    # Yeni mesajı ekle
    user_messages[guild_id][user_id].append(now)
    
    # Flood kontrolü
    return len(user_messages[guild_id][user_id]) > limit


async def handle_level_up(guild: discord.Guild, user: discord.Member, old_level: int, new_level: int):
    if old_level >= new_level:
        return
        
    config = get_level_config(guild.id)
    if not config:
        return
    
    # Level rol atama
    for req_level, role_key in LEVEL_ROLES.items():
        role_id = config.get(role_key)
        if role_id and new_level >= req_level:
            role = guild.get_role(role_id)
            if role and role not in user.roles:
                try:
                    await user.add_roles(role, reason=f"Level {req_level} rolü")
                except Exception as e:
                    print(f"{Fore.RED}Rol verme hatası: {e}{Style.RESET_ALL}")
    
    # Level atlama duyurusu
    announcement_channel_ids = config.get("announcement_channel_ids", [])
    log_channel_id = config.get("log_channel_id")
    
    embed = discord.Embed(
        title="🎉 Level Atladın!",
        description=f"{user.mention} **Level {new_level}** oldu!",
        color=discord.Color.gold(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    
    # Duyuru kanallarına gönder
    for channel_id in announcement_channel_ids:
        channel = guild.get_channel(channel_id)
        if channel:
            try:
                await channel.send(embed=embed)
            except Exception as e:
                print(f"{Fore.RED}Duyuru kanalına gönderim hatası: {e}{Style.RESET_ALL}")
    
    # Log kanalına gönder
    if log_channel_id:
        log_channel = guild.get_channel(log_channel_id)
        if log_channel:
            try:
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"{Fore.RED}Log kanalına gönderim hatası: {e}{Style.RESET_ALL}")

# --- Events ---
@bot.event
async def on_ready():
    print(f"{Fore.GREEN}{bot.user} olarak giriş yapıldı!{Style.RESET_ALL}")
    initialize_database()
    try:
        synced = await tree.sync()
        print(f"{Fore.GREEN}{len(synced)} komut senkronize edildi.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Komut senkronizasyon hatası: {e}{Style.RESET_ALL}")

@bot.event
async def on_member_join(member):
    try:
        role_id = get_autorole(member.guild.id)
        if not role_id: return
        
        role = member.guild.get_role(role_id)
        if role:
            await member.add_roles(role, reason="OtoRol Sistemi")
    except Exception as e:
        print(f"{Fore.RED}Otorol verme hatası: {e}{Style.RESET_ALL}")

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        await bot.process_commands(message)
        return

    guild_id = message.guild.id
    user_id = message.author.id
    content = message.content.lower()

    # Immune kullanıcı kontrolü
    if is_immune(guild_id, user_id):
        await bot.process_commands(message)
        return

    # XP Sistemi
    current_time = time.time()
    last_xp_time = None
    
    # Son mesaj zamanını kontrol et
    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            c.execute("""
                SELECT last_message_time 
                FROM user_levels 
                WHERE guild_id=? AND user_id=?
            """, (guild_id, user_id))
            result = c.fetchone()
            last_xp_time = result[0] if result else None
        except Error:
            pass
        finally:
            conn.close()
    
    # XP kazanma kontrolü
    should_gain_xp = True
    if last_xp_time and (current_time - last_xp_time) < XP_COOLDOWN:
        should_gain_xp = False
    
    # XP ver
    if should_gain_xp:
        xp, level = get_user_level(guild_id, user_id)
        new_xp = xp + XP_PER_MESSAGE
        new_level = calculate_level(new_xp)
        
        # Level atlama kontrolü
        if new_level > level:
            await handle_level_up(message.guild, message.author, level, new_level)
        
        set_user_level(guild_id, user_id, new_xp, new_level, current_time)

    # Küfür kontrolü
    if any(kufur in content.split() for kufur in kufurler):
        try:
            await message.delete()
        except Exception as e:
            print(f"{Fore.RED}Mesaj silme hatası: {e}{Style.RESET_ALL}")

        # Uyarı ekle
        count = add_warning(guild_id, user_id)
        add_mod_history(guild_id, user_id, "UYARI", bot.user.id, "Küfür tespit edildi")

        # XP cezası
        new_xp, _ = update_user_xp(guild_id, user_id, -XP_PENALTY)
        
        # Uyarı embedi
        embed = embed_message(
            title="🚨 Küfür Tespit Edildi!",
            description=f"{message.author.mention} adlı kullanıcı küfür etti ve uyarıldı.\n"
                        f"Toplam uyarı: **{count}**\n"
                        f"XP cezası: **-{XP_PENALTY} XP** (Yeni XP: {new_xp})",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed, delete_after=10)
        await log_gonder(guild_id, embed)

        # Uyarı sınırı aşılırsa mute
        if count >= warn_limit:
            if message.guild.me.guild_permissions.moderate_members:
                try:
                    await message.author.timeout(duration=mute_duration)
                    add_mod_history(guild_id, user_id, "MUTE", bot.user.id, "3 uyarı sınırı aşımı")
                    
                    embed2 = embed_message(
                        title="🔇 Kullanıcı Susturuldu",
                        description=f"{message.author.mention} {mute_duration.total_seconds()//60} dakika boyunca susturuldu (3 uyarı sınırı aşımı).",
                        color=discord.Color.orange()
                    )
                    await message.channel.send(embed=embed2)
                    await log_gonder(guild_id, embed2)
                    
                    # Uyarıları sıfırla
                    conn = create_connection()
                    if conn:
                        try:
                            c = conn.cursor()
                            c.execute("""
                                UPDATE warnings 
                                SET count=0 
                                WHERE guild_id=? AND user_id=?
                            """, (guild_id, user_id))
                            conn.commit()
                        except Error as e:
                            print(f"{Fore.RED}Uyarı sıfırlama hatası: {e}{Style.RESET_ALL}")
                        finally:
                            conn.close()
                except Exception as e:
                    print(f"{Fore.RED}Susturma hatası: {e}{Style.RESET_ALL}")

    # Flood kontrolü
    elif is_flood(guild_id, user_id):
        try:
            await message.delete()
        except Exception as e:
            print(f"{Fore.RED}Mesaj silme hatası: {e}{Style.RESET_ALL}")
        
        # XP cezası
        new_xp, _ = update_user_xp(guild_id, user_id, -XP_PENALTY)
        
        embed = embed_message(
            title="⚠️ Flood Koruması",
            description=f"{message.author.mention} flood yapmaya çalıştı, mesaj silindi.\n"
                        f"XP cezası: **-{XP_PENALTY} XP** (Yeni XP: {new_xp})",
            color=discord.Color.gold()
        )
        await message.channel.send(embed=embed, delete_after=10)
        await log_gonder(guild_id, embed)

    # Reklam/link kontrolü
    if "http://" in content or "https://" in content or "discord.gg/" in content:
        if not is_immune(guild_id, user_id):
            try:
                await message.delete()
            except Exception as e:
                print(f"{Fore.RED}Mesaj silme hatası: {e}{Style.RESET_ALL}")
            
            # XP cezası
            new_xp, _ = update_user_xp(guild_id, user_id, -XP_PENALTY)
            
            embed = embed_message(
                title="🚫 Reklam Engellendi",
                description=f"{message.author.mention} reklam/link paylaştığı için mesajı silindi.\n"
                            f"XP cezası: **-{XP_PENALTY} XP** (Yeni XP: {new_xp})",
                color=discord.Color.dark_red()
            )
            await message.channel.send(embed=embed, delete_after=10)
            await log_gonder(guild_id, embed)

    # AFK kontrolü
    for mention in message.mentions:
        if mention.id in afk_users:
            afk_msg, afk_time = afk_users[mention.id]
            delta = datetime.now(timezone.utc) - afk_time
            dakika = int(delta.total_seconds() // 60)
            afk_embed = discord.Embed(
                title="⏰ AFK Kullanıcı",
                description=f"{mention.display_name} şu anda AFK.\nMesaj: {afk_msg}\nAFK süresi: {dakika} dk",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            await message.channel.send(embed=afk_embed)

    if message.author.id in afk_users:
        del afk_users[message.author.id]
        geri_embed = discord.Embed(
            title="👋 Hoş Geldin",
            description="AFK modundan çıktın.",
            color=discord.Color.green(),
            timestamp=datetime.now(timezone.utc))
        await message.channel.send(embed=geri_embed)

    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.guild:
        return

    # Çift loglama önleme
    if message.id in deleted_messages:
        deleted_messages.remove(message.id)
        return

    # Veritabanına kaydet
    log_message(
        guild_id=message.guild.id,
        channel_id=message.channel.id,
        user_id=message.author.id,
        message_id=message.id,
        content=message.content,
        attachments=message.attachments,
        is_deleted=True
    )

    log_channel_id = get_log_channel(message.guild.id)
    if not log_channel_id:
        return

    log_channel = bot.get_channel(log_channel_id)
    if not log_channel:
        return

    content = message.content
    if content and len(content) > 1024:
        content = content[:1021] + "..."

    embed = discord.Embed(
        title="🗑️ Mesaj Silindi",
        color=discord.Color.red(),
        timestamp=datetime.now(timezone.utc))
    embed.add_field(name="Kanal", value=message.channel.mention, inline=True)
    embed.add_field(name="Kullanıcı", value=message.author.mention, inline=True)
    embed.add_field(name="Mesaj ID", value=message.id, inline=True)
    embed.add_field(
        name="Silinen Mesaj", 
        value=content or "*[İçerik yok]*", 
        inline=False)
    
    if message.attachments:
        embed.add_field(
            name="Ekler", 
            value="\n".join([f"[{a.filename}]({a.url})" for a in message.attachments]),
            inline=False)

    try:
        await log_channel.send(embed=embed)
    except Exception as e:
        print(f"{Fore.RED}Log gönderilirken hata oluştu: {e}{Style.RESET_ALL}")

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or not before.guild or before.content == after.content:
        return

    # Veritabanına kaydet
    log_message(
        guild_id=before.guild.id,
        channel_id=before.channel.id,
        user_id=before.author.id,
        message_id=before.id,
        content=f"{before.content}\n\n**DÜZENLENDİ:**\n{after.content}",
        is_edited=True
    )

    log_channel_id = get_log_channel(before.guild.id)
    if not log_channel_id:
        return

    log_channel = bot.get_channel(log_channel_id)
    if not log_channel:
        return

    before_content = before.content
    after_content = after.content
    if before_content and len(before_content) > 500:
        before_content = before_content[:497] + "..."
    if after_content and len(after_content) > 500:
        after_content = after_content[:497] + "..."

    embed = discord.Embed(
        title="✏️ Mesaj Düzenlendi",
        color=discord.Color.orange(),
        timestamp=datetime.now(timezone.utc))
    embed.add_field(name="Kanal", value=before.channel.mention, inline=True)
    embed.add_field(name="Kullanıcı", value=before.author.mention, inline=True)
    embed.add_field(name="Mesaj ID", value=before.id, inline=True)
    embed.add_field(name="Orijinal Mesaj", value=before_content or "*[İçerik yok]*", inline=False)
    embed.add_field(name="Düzenlenmiş Mesaj", value=after_content or "*[İçerik yok]*", inline=False)
    
    try:
        await log_channel.send(embed=embed)
    except Exception as e:
        print(f"{Fore.RED}Log gönderilirken hata oluştu: {e}{Style.RESET_ALL}")

# --- Yetki Kontrol Fonksiyonu ---
def is_admin_or_owner(interaction: discord.Interaction):
    return interaction.user.guild_permissions.administrator or interaction.user.id in OWNER_IDS

# --- Slash Commands ---
@tree.command(name="ping", description="Botun gecikmesini gösterir.")
async def ping(interaction: discord.Interaction):
    try:
        await interaction.response.send_message(f"Pong! 🏓 {round(bot.latency * 1000)}ms")
    except Exception as e:
        await interaction.response.send_message("Ping komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Ping komutu hatası: {e}{Style.RESET_ALL}")


@tree.command(name="durum", description="Botun durum mesajını değiştirir (sadece admin).")
@app_commands.describe(tur="Durum tipi", mesaj="Durumda görünecek metin")
async def durum(interaction: discord.Interaction, tur: str, mesaj: str):
    try:
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.", ephemeral=True)
            return

        tur_map = {
            "oynuyor": discord.ActivityType.playing,
            "izliyor": discord.ActivityType.watching,
            "dinliyor": discord.ActivityType.listening,
            "yayında": discord.ActivityType.streaming
        }

        if tur.lower() not in tur_map:
            await interaction.response.send_message(
                "Geçerli türler: oynuyor, izliyor, dinliyor, yayında",
                ephemeral=True
            )
            return

        await bot.change_presence(
            activity=discord.Activity(
                type=tur_map[tur.lower()],
                name=mesaj
            )
        )

        await interaction.response.send_message(f"✅ Durum **{tur} {mesaj}** olarak ayarlandı.")
    except Exception as e:
        await interaction.response.send_message("Durum komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Durum komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="logkanal", description="Log kanalı ayarla")
@app_commands.describe(channel="Logların gönderileceği kanal")
async def logkanal(interaction: discord.Interaction, channel: discord.TextChannel):
    try:
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.", ephemeral=True)
            return
        set_log_channel(interaction.guild_id, channel.id)
        await interaction.response.send_message(f"Log kanalı başarıyla {channel.mention} olarak ayarlandı.")
    except Exception as e:
        await interaction.response.send_message("Logkanal komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Logkanal komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="uyarilar", description="Bir kullanıcının uyarı sayısını gösterir.")
@app_commands.describe(user="Uyarılarını görmek istediğin kişi")
async def uyarilar(interaction: discord.Interaction, user: discord.Member):
    try:
        count = get_warnings(interaction.guild_id, user.id)
        embed = embed_message(
            title=f"{user} adlı kullanıcının uyarıları",
            description=f"Toplam uyarı sayısı: **{count}**",
            color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message("Uyarılar komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Uyarılar komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="warn", description="Bir kullanıcıya manuel uyarı ver.")
@app_commands.describe(user="Uyarı verilecek kişi", reason="Uyarı sebebi")
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str = "Sebep belirtilmedi"):
    try:
        if not interaction.user.guild_permissions.kick_members and interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.", ephemeral=True)
            return

        count = add_warning(interaction.guild_id, user.id)
        add_mod_history(interaction.guild_id, user.id, "UYARI", interaction.user.id, reason)

        # XP cezası
        new_xp, _ = update_user_xp(interaction.guild_id, user.id, -XP_PENALTY)
        
        embed = embed_message(
            title="⚠️ Manuel Uyarı Verildi",
            description=f"{user.mention} adlı kullanıcıya uyarı verildi.\n"
                        f"Sebep: {reason}\n"
                        f"Toplam uyarı: **{count}**\n"
                        f"XP cezası: **-{XP_PENALTY} XP** (Yeni XP: {new_xp})",
            color=discord.Color.orange())
        await interaction.response.send_message(embed=embed)
        await log_gonder(interaction.guild_id, embed)
    except Exception as e:
        await interaction.response.send_message("Warn komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Warn komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="uyarisil", description="Bir kullanıcının uyarısını siler.")
@app_commands.describe(user="Uyarısı silinecek kişi")
async def uyarisil(interaction: discord.Interaction, user: discord.Member):
    try:
        if not interaction.user.guild_permissions.kick_members and interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.", ephemeral=True)
            return
        removed = remove_warning(interaction.guild_id, user.id)
        if removed:
            add_mod_history(interaction.guild_id, user.id, "UYARI_SIL", interaction.user.id)
            await interaction.response.send_message(f"{user.mention} adlı kullanıcının bir uyarısı silindi.")
        else:
            await interaction.response.send_message(f"{user.mention} adlı kullanıcının uyarısı bulunamadı.")
    except Exception as e:
        await interaction.response.send_message("Uyarısil komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Uyarısil komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="clear", description="Kanaldaki mesajları temizler.")
@app_commands.describe(amount="Silinecek mesaj sayısı (max 100)")
async def clear(interaction: discord.Interaction, amount: int):
    try:
        if not interaction.user.guild_permissions.manage_messages and interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.", ephemeral=True)
            return
        if amount < 1 or amount > 100:
            await interaction.response.send_message("Lütfen 1 ile 100 arasında bir sayı girin.", ephemeral=True)
            return
        
        # Geçmiş mesajları al ve sil
        deleted = await interaction.channel.purge(limit=amount)
        
        # Silinen mesajları veritabanına kaydet ve çift log önle
        for msg in deleted:
            deleted_messages.add(msg.id)  # Çift log önleme için ekle
            if not msg.author.bot:
                log_message(
                    guild_id=interaction.guild_id,
                    channel_id=msg.channel.id,
                    user_id=msg.author.id,
                    message_id=msg.id,
                    content=msg.content,
                    attachments=msg.attachments,
                    is_deleted=True,
                    moderator_id=interaction.user.id
                )
        
        embed = embed_message(
            title="🧹 Mesajlar Temizlendi",
            description=f"{interaction.user.mention}, {len(deleted)} mesajı sildi.",
            color=discord.Color.dark_gold())
        await log_gonder(interaction.guild_id, embed)
        await interaction.response.send_message(f"{len(deleted)} mesaj silindi.", ephemeral=True, delete_after=5)
    except Exception as e:
        await interaction.response.send_message("Clear komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Clear komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="mute", description="Bir kullanıcıyı belirli süre susturur.")
@app_commands.describe(user="Susturulacak kullanıcı", sure="Süre örn: 10s, 1h, 1d, 1w")
async def mute(interaction: discord.Interaction, user: discord.Member, sure: str):
    try:
        if not interaction.user.guild_permissions.moderate_members and interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.", ephemeral=True)
            return
        duration = parse_duration(sure)
        await user.timeout(datetime.now(timezone.utc) + duration)
        add_mod_history(interaction.guild_id, user.id, "MUTE", interaction.user.id, sure)
        
        embed = embed_message(
            title="🔇 Kullanıcı Susturuldu",
            description=f"{user.mention} {sure} boyunca susturuldu.\nYetkili: {interaction.user.mention}",
            color=discord.Color.orange())
        await log_gonder(interaction.guild_id, embed)
        await interaction.response.send_message(f"{user.mention} {sure} boyunca susturuldu.")
    except ValueError as e:
        await interaction.response.send_message(f"Hata: {e}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Beklenmeyen hata: {e}", ephemeral=True)
        print(f"{Fore.RED}Mute komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="unmute", description="Bir kullanıcının susturmasını kaldırır.")
@app_commands.describe(user="Susturması kaldırılacak kullanıcı")
async def unmute(interaction: discord.Interaction, user: discord.Member):
    try:
        if not interaction.user.guild_permissions.moderate_members and interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.", ephemeral=True)
            return
        await user.timeout(None)
        add_mod_history(interaction.guild_id, user.id, "UNMUTE", interaction.user.id)
        
        embed = embed_message(
            title="🔊 Susturma Kaldırıldı",
            description=f"{user.mention} adlı kullanıcının susturması kaldırıldı.\nYetkili: {interaction.user.mention}",
            color=discord.Color.green())
        await log_gonder(interaction.guild_id, embed)
        await interaction.response.send_message(f"{user.mention} artık susturulmadı.")
    except Exception as e:
        await interaction.response.send_message(f"Hata: {e}", ephemeral=True)
        print(f"{Fore.RED}Unmute komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="ban", description="Bir kullanıcıyı sunucudan banlar.")
@app_commands.describe(user="Banlanacak kullanıcı", reason="Ban sebebi (isteğe bağlı)")
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Sebep belirtilmedi"):
    try:
        if not interaction.user.guild_permissions.ban_members and interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.", ephemeral=True)
            return
        await interaction.guild.ban(user, reason=reason)
        add_mod_history(interaction.guild_id, user.id, "BAN", interaction.user.id, reason)
        
        embed = embed_message(
            title="⛔ Kullanıcı Banlandı",
            description=f"{user.mention} sunucudan banlandı.\nSebep: {reason}\nYetkili: {interaction.user.mention}",
            color=discord.Color.red())
        await log_gonder(interaction.guild_id, embed)
        await interaction.response.send_message(f"{user.mention} sunucudan banlandı. Sebep: {reason}")
    except Exception as e:
        await interaction.response.send_message(f"Hata: {e}", ephemeral=True)
        print(f"{Fore.RED}Ban komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="avatar", description="Bir kullanıcının avatarını gösterir.")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    try:
        user = user or interaction.user
        embed = discord.Embed(
            title=f"{user}'ın Avatarı",
            color=discord.Color.blurple(),
            timestamp=datetime.now(timezone.utc))
        embed.set_image(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message("Avatar komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Avatar komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="kullanici", description="Bir kullanıcı hakkında bilgi verir.")
async def kullanici(interaction: discord.Interaction, user: discord.Member = None):
    try:
        user = user or interaction.user
        xp, level = get_user_level(interaction.guild_id, user.id)
        
        embed = discord.Embed(
            title=f"{user} hakkında bilgi", 
            color=discord.Color.green(), 
            timestamp=datetime.now(timezone.utc))
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="İsim", value=user.name, inline=True)
        embed.add_field(name="Etiket", value=user.discriminator, inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Level", value=f"{level} (XP: {xp})", inline=True)
        embed.add_field(name="Hesap oluşturma", value=user.created_at.strftime("%d.%m.%Y %H:%M"), inline=True)
        embed.add_field(name="Sunucuya katılma", value=user.joined_at.strftime("%d.%m.%Y %H:%M") if user.joined_at else "Bilinmiyor", inline=True)
        embed.add_field(name="Bot mu?", value=str(user.bot), inline=True)
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message("Kullanıcı komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Kullanıcı komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="sunucu", description="Sunucu hakkında genel bilgileri gösterir.")
async def sunucu(interaction: discord.Interaction):
    try:
        guild = interaction.guild
        bot_count = sum(1 for m in guild.members if m.bot)

        embed = discord.Embed(
            title="📡 Sunucu Bilgisi",
            color=discord.Color.blurple(),
            timestamp=datetime.now(timezone.utc))
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="📛 İsim", value=guild.name, inline=True)
        embed.add_field(name="🆔 ID", value=guild.id, inline=True)
        embed.add_field(name="👑 Sahip", value=guild.owner.mention, inline=True)
        embed.add_field(name="🧑‍🤝‍🧑 Toplam Üye", value=guild.member_count, inline=True)
        embed.add_field(name="🤖 Botlar", value=bot_count, inline=True)
        embed.add_field(name="📆 Oluşturulma", value=guild.created_at.strftime("%d.%m.%Y %H:%M"), inline=False)
        embed.add_field(name="🔒 Doğrulama", value=str(guild.verification_level), inline=True)
        embed.add_field(name="📝 Roller", value=len(guild.roles), inline=True)

        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message("Sunucu komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Sunucu komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="otorol", description="Sunucuya girenlere verilecek rolü ayarlar.")
@app_commands.describe(rol="Otomatik verilecek rol")
async def otorol(interaction: discord.Interaction, rol: discord.Role):
    try:
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.", ephemeral=True)
            return
        set_autorole(interaction.guild_id, rol.id)
        await interaction.response.send_message(f"Artık sunucuya girenlere {rol.mention} rolü otomatik olarak verilecek.")
    except Exception as e:
        await interaction.response.send_message("Otorol komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Otorol komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="sarki", description="Rastgele bir şarkı önerir.")
async def sarki(interaction: discord.Interaction):
    try:
        sarkilar = [
            "Dolu Kadehi Ters Tut - Sedef Sebülktekin",
            "Her Şeyi Yak - Duman",
            "Belki Alışman Lazım - Duman",
            "Müneccim - İkra, Kayra",
            "Herkes Kadar Kimse - Kayra",
            "Arafta Bile - Kayra",
            "Kayıp Gölgeler - Kayra",
            "Şaraplar ve Kadınlar - Mert Şenel",
            "Çok Yaşlıyım - Kayra",
            "Bütün Ayazların Ortasında - Kayra",
            "Keder - Yaşlı Amca",
            "Ve Ben - Yaşlı Amca",
            "Akşamüstü - Yaşlı Amca",
            "Hikaye Bitti Çoktan - Kayra",
            "Ömrümün Son Güzel Günleri - Kayra",
            "Seni Kendime Sakladım - Duman",
            "Nerdesin - Lotusx",
            "Uzun İnce Bir Yoldayım - Aşık Veysel",
            "Yıldızların Altında - Kargo",
            "Doldum - Adamlar",
            "Moonlight - XXXTENTACION",
            "Bu Akşam - Duman",
            "24 - Sagopa Kajmer",
            "Aman Aman - Duman",
            "Giderdi Hoşuma - Yaşlı Amca",
            "Kafam Senden Bile Güzel - Kolpa",
            "Revenge - XXXTENTACION",
            "Ama Bana Bakma Öyle - VAGON",
            "Nilüfer - Yaşlı Amca",
            "Yakamoz Güzeli - Yaşlı Amca",
            "İstanbul Beyefendisi - Yaşlı Amca",
            "Yürek - Duman",
            "Cevapsız Sorular - manga","Serseri  -Teoman","İki Yabancı - Teoman","Anlıyorsun Değil Mi - Teoman","Bu Benim Hayatım - No.1","Yalnızlık","Aşırı Doz Melankoli -No1","Bi Gece- No1","Dünya Gül Bana - No1","Gün Size Günaydı","Yalan Olur - No1","Aşk-ı Masal - No1"
        ]
        secilen = random.choice(sarkilar)
        embed = discord.Embed(
            title="🎶 Şarkı Önerisi",
            description=f"Bugünün önerisi: **{secilen}**",
            color=discord.Color.purple(),
            timestamp=datetime.now(timezone.utc))
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message("Şarkı komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Şarkı komutu hatası: {e}{Style.RESET_ALL}")

# --- AFK Sistemi ---
@tree.command(name="afk", description="AFK moduna geçersiniz. Biri sizi etiketlediğinde bilgi verilir.")
@app_commands.describe(mesaj="AFK mesajınız")
async def afk(interaction: discord.Interaction, mesaj: str = "Şu anda AFK'yım."):
    try:
        afk_users[interaction.user.id] = (mesaj, datetime.now(timezone.utc))
        embed = discord.Embed(
            title="📴 AFK Modu",
            description=f"{interaction.user.mention} artık AFK modunda.\nMesaj: {mesaj}",
            color=discord.Color.dark_grey(),
            timestamp=datetime.now(timezone.utc))
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message("AFK komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}AFK komutu hatası: {e}{Style.RESET_ALL}")

# --- Oylama Sistemi ---
@tree.command(name="oylama", description="Emojiyle oylama başlatır.")
async def oylama(interaction: discord.Interaction, soru: str):
    try:
        embed = discord.Embed(
            title="🗳️ Yeni Oylama",
            description=f"**{soru}**\n\n✅: Evet\n❌: Hayır",
            color=discord.Color.teal(),
            timestamp=datetime.now(timezone.utc))
        embed.set_footer(text=f"Oylamayı başlatan: {interaction.user}")
        mesaj = await interaction.channel.send(embed=embed)
        await mesaj.add_reaction("✅")
        await mesaj.add_reaction("❌")
        await interaction.response.send_message("Oylama başlatıldı!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message("Oylama komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Oylama komutu hatası: {e}{Style.RESET_ALL}")

# --- OP Sistemi ---
@tree.command(name="op", description="Kullanıcıyı moderasyon korumalarından muaf tutar (sadece admin)")
@app_commands.describe(user="Muaf tutulacak kullanıcı")
async def op(interaction: discord.Interaction, user: discord.Member):
    try:
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.", ephemeral=True)
            return
        
        add_immune_user(interaction.guild_id, user.id)
        embed = embed_message(
            title="🛡️ Kullanıcı Muaf Edildi",
            description=f"{user.mention} artık moderasyon korumalarından muaf.\nKüfür, reklam ve flood korumaları bu kullanıcı için uygulanmayacak.",
            color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
        await log_gonder(interaction.guild_id, embed)
    except Exception as e:
        await interaction.response.send_message("OP komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}OP komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="unop", description="Kullanıcının moderasyon muafiyetini kaldırır (sadece admin)")
@app_commands.describe(user="Muafiyeti kaldırılacak kullanıcı")
async def unop(interaction: discord.Interaction, user: discord.Member):
    try:
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.", ephemeral=True)
            return
        
        removed = remove_immune_user(interaction.guild_id, user.id)
        if removed:
            embed = embed_message(
                title="⚠️ Muafiyet Kaldırıldı",
                description=f"{user.mention} artık moderasyon korumalarına tabi.\nKüfür, reklam ve flood korumaları bu kullanıcı için tekrar etkin.",
                color=discord.Color.orange())
            await interaction.response.send_message(embed=embed)
            await log_gonder(interaction.guild_id, embed)
        else:
            await interaction.response.send_message(f"{user.mention} zaten muaf değil.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message("Unop komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Unop komutu hatası: {e}{Style.RESET_ALL}")

# --- Öneri Sistemi ---
@tree.command(name="oneri", description="Bot için öneride bulunun")
@app_commands.describe(öneri="Bot için öneriniz")
async def oneri(interaction: discord.Interaction, öneri: str):
    try:
        suggestion_id = add_suggestion(interaction.guild_id, interaction.user.id, öneri)
        if suggestion_id:
            embed = embed_message(
                title="💡 Öneri Gönderildi",
                description=f"Öneriniz başarıyla kaydedildi!\nID: `{suggestion_id}`\nÖneriniz: {öneri}",
                color=discord.Color.blue())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("Öneri gönderilirken bir hata oluştu.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message("Öneri komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Öneri komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="oneriler", description="Sunucuya gönderilen önerileri listeler (sadece admin)")
async def oneriler(interaction: discord.Interaction):
    try:
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.", ephemeral=True)
            return
        
        suggestions = get_suggestions(interaction.guild_id)
        if not suggestions:
            await interaction.response.send_message("Henüz hiç öneri gönderilmemiş.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📝 Öneriler Listesi",
            description=f"Toplam {len(suggestions)} öneri bulundu:",
            color=discord.Color.blurple())
        
        for sug in suggestions:
            user = interaction.guild.get_member(sug[1])
            username = user.display_name if user else f"ID: {sug[1]}"
            embed.add_field(
                name=f"ID: {sug[0]} | {username} - {sug[3]}",
                value=sug[2],
                inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message("Öneriler komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Öneriler komutu hatası: {e}{Style.RESET_ALL}")

# --- Mod Geçmişi ---
@tree.command(name="history", description="Kullanıcının mod geçmişini gösterir (sadece admin)")
@app_commands.describe(user="Geçmişi görüntülenecek kullanıcı")
async def history(interaction: discord.Interaction, user: discord.Member):
    try:
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.", ephemeral=True)
            return
        
        history = get_mod_history(interaction.guild_id, user.id)
        if not history:
            await interaction.response.send_message(f"{user.mention} adlı kullanıcının geçmişinde hiç mod işlemi bulunamadı.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📜 {user} Mod Geçmişi",
            description=f"Toplam {len(history)} işlem bulundu:",
            color=discord.Color.dark_grey())
        
        for i, (action, reason, mod_id, timestamp) in enumerate(history, 1):
            moderator = interaction.guild.get_member(mod_id)
            mod_name = moderator.display_name if moderator else f"ID: {mod_id}"
            embed.add_field(
                name=f"{i}. {action} - {timestamp}",
                value=f"**Yetkili:** {mod_name}\n**Sebep:** {reason or 'Belirtilmemiş'}",
                inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message("History komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}History komutu hatası: {e}{Style.RESET_ALL}")

# --- Level Sistemi Komutları ---
@tree.command(name="levelsistemi", description="Level sistemini ayarlar (sadece admin)")
@app_commands.describe(
    role1="Level 1 için rol",
    role2="Level 2 için rol",
    role3="Level 3 için rol",
    kanal1="Level duyuru kanalı 1 (isteğe bağlı)",
    kanal2="Level duyuru kanalı 2 (isteğe bağlı)",
    kanal3="Level duyuru kanalı 3 (isteğe bağlı)",
    log_kanal="Level log kanalı (isteğe bağlı)"
)
async def levelsistemi(
    interaction: discord.Interaction, 
    role1: discord.Role, 
    role2: discord.Role, 
    role3: discord.Role, 
    kanal1: discord.TextChannel = None, 
    kanal2: discord.TextChannel = None, 
    kanal3: discord.TextChannel = None,
    log_kanal: discord.TextChannel = None
):
    try:
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.", ephemeral=True)
            return
        
        # Kanal ID'lerini topla
        announcement_channels = []
        if kanal1: announcement_channels.append(kanal1.id)
        if kanal2: announcement_channels.append(kanal2.id)
        if kanal3: announcement_channels.append(kanal3.id)
        
        log_channel_id = log_kanal.id if log_kanal else None
        
        # Veritabanına kaydet
        set_level_config(
            interaction.guild_id,
            role1.id,
            role2.id,
            role3.id,
            announcement_channels,
            log_channel_id
        )
        
        # Yanıt oluştur
        description = f"**Level Rolleri:**\n" \
                     f"Level 1: {role1.mention}\n" \
                     f"Level 2: {role2.mention}\n" \
                     f"Level 3: {role3.mention}\n\n" \
                     f"**Duyuru Kanalları:**\n"
        
        if announcement_channels:
            for ch_id in announcement_channels:
                channel = interaction.guild.get_channel(ch_id)
                if channel:
                    description += f"- {channel.mention}\n"
        else:
            description += "Ayarlanmadı\n"
        
        description += f"\n**Log Kanalı:** {log_kanal.mention if log_kanal else 'Ayarlanmadı'}"
        
        embed = embed_message(
            title="✅ Level Sistemi Ayarları",
            description=description,
            color=discord.Color.green())
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message("Levelsistemi komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Levelsistemi komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="level", description="Kullanıcının level ve XP bilgisini gösterir")
@app_commands.describe(user="Bilgisi görüntülenecek kullanıcı (isteğe bağlı)")
async def level(interaction: discord.Interaction, user: discord.Member = None):
    try:
        user = user or interaction.user
        xp, level = get_user_level(interaction.guild_id, user.id)
        next_level_xp = xp_for_level(level + 1)
        progress = min(100, int((xp / next_level_xp) * 100)) if next_level_xp > 0 else 0
        
        # Progress bar oluştur
        progress_bar = "[" + "■" * (progress // 10) + "□" * (10 - (progress // 10)) + "]"
        
        embed = discord.Embed(
            title=f"📊 {user.display_name} Level Bilgisi",
            color=discord.Color.blurple(),
            timestamp=datetime.now(timezone.utc))
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Level", value=str(level), inline=True)
        embed.add_field(name="XP", value=str(xp), inline=True)
        embed.add_field(name="Sonraki Level", value=f"{next_level_xp} XP", inline=True)
        embed.add_field(name="İlerleme", value=f"{progress_bar} {progress}%", inline=False)
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message("Level komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Level komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="level-sifirla", description="Kullanıcının level ve XP bilgisini sıfırlar (sadece admin)")
@app_commands.describe(user="Sıfırlanacak kullanıcı")
async def level_sifirla(interaction: discord.Interaction, user: discord.Member):
    try:
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.", ephemeral=True)
            return
        
        set_user_level(interaction.guild_id, user.id, 0, 0)
        embed = embed_message(
            title="🔄 Level Sıfırlandı",
            description=f"{user.mention} adlı kullanıcının level ve XP bilgileri sıfırlandı.",
            color=discord.Color.orange())
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message("Level-sifirla komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Level-sifirla komutu hatası: {e}{Style.RESET_ALL}")

# --- Dil Rol Sistemi ---
@tree.command(name="language", description="Dil rol sistemini ayarlar")
@app_commands.describe(
    tr_role="Türkçe rolü",
    en_role="İngilizce rolü",
    other_role="Diğer diller için rol"
)
async def language(
    interaction: discord.Interaction, 
    tr_role: discord.Role, 
    en_role: discord.Role, 
    other_role: discord.Role
):
    try:
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.", ephemeral=True)
            return
        
        set_language_roles(interaction.guild_id, tr_role.id, en_role.id, other_role.id)
        
        # Embed oluştur
        embed = discord.Embed(
            title="🌍 Dil Rol Sistemi",
            description="Kullanıcılar aşağıdaki butonlara tıklayarak dil rollerini seçebilirler.",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="Türkçe", value=tr_role.mention, inline=True)
        embed.add_field(name="İngilizce", value=en_role.mention, inline=True)
        embed.add_field(name="Diğer Diller", value=other_role.mention, inline=True)
        embed.set_footer(text="Lütfen iletişim dilinizi seçin")
        
        # Butonlu view oluştur
        view = LanguageSelect({
            "role_tr": tr_role.id,
            "role_en": en_role.id,
            "role_other": other_role.id
        })
        
        await interaction.response.send_message(embed=embed, view=view)
    except Exception as e:
        await interaction.response.send_message("Language komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Language komutu hatası: {e}{Style.RESET_ALL}")

# --- Mesaj Logları Komutu ---
@tree.command(name="logs", description="Kullanıcının mesaj loglarını gösterir (sadece admin)")
@app_commands.describe(user="Logları görüntülenecek kullanıcı", limit="Gösterilecek log sayısı (max 20)")
async def logs(interaction: discord.Interaction, user: discord.Member, limit: int = 5):
    try:
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.", ephemeral=True)
            return
            
        if limit < 1 or limit > 20:
            await interaction.response.send_message("Lütfen 1 ile 20 arasında bir sayı girin.", ephemeral=True)
            return
            
        logs = get_message_logs(interaction.guild_id, user.id, limit)
        if not logs:
            await interaction.response.send_message(f"{user.mention} adlı kullanıcıya ait mesaj logu bulunamadı.", ephemeral=True)
            return
            
        embed = discord.Embed(
            title=f"📜 {user} Mesaj Logları",
            description=f"Son {len(logs)} mesaj aktivitesi:",
            color=discord.Color.dark_grey(),
            timestamp=datetime.now(timezone.utc))
        
        for log in logs:
            log_id, guild_id, channel_id, user_id, message_id, content, attachments, is_deleted, is_edited, moderator_id, timestamp = log
            
            action = ""
            if is_deleted:
                action = "🗑️ Silindi"
            elif is_edited:
                action = "✏️ Düzenlendi"
                
            mod_text = ""
            if moderator_id:
                mod = interaction.guild.get_member(moderator_id)
                mod_text = f" | Yetkili: {mod.mention if mod else f'ID: {moderator_id}'}"
                
            channel = interaction.guild.get_channel(channel_id)
            channel_text = f"#{channel.name}" if channel else f"Kanal ID: {channel_id}"
            
            # İçeriği kısalt
            if content and len(content) > 200:
                content = content[:197] + "..."
                
            embed.add_field(
                name=f"{action} | {timestamp} | {channel_text}{mod_text}",
                value=content or "*[İçerik yok]*",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message("Logs komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Logs komutu hatası: {e}{Style.RESET_ALL}")

# --- Sunucu Kurulum Komutu ---
@tree.command(name="sunucu-kur", description="Sunucu için temel yapıyı kurar (kanallar, roller, izinler)")
async def sunucu_kur(interaction: discord.Interaction):
    try:
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("Bu komutu sadece sunucu sahibi veya yöneticiler kullanabilir.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        # Rolleri oluştur
        # Yönetici rolü (tüm yetkiler)
        admin_role = await guild.create_role(
            name="Admin",
            permissions=discord.Permissions.all(),
            reason="Sunucu kurulumu"
        )
        
        # Moderatör rolü (temel moderasyon yetkileri)
        mod_role = await guild.create_role(
            name="Moderatör",
            permissions=discord.Permissions(
                manage_messages=True,
                kick_members=True,
                ban_members=True,
                moderate_members=True,
                manage_channels=True
            ),
            reason="Sunucu kurulumu"
        )
        
        # Rehber rolü (yardım yetkileri)
        rehber_role = await guild.create_role(
            name="Rehber",
            permissions=discord.Permissions(
                send_messages=True,
                read_message_history=True,
                mention_everyone=True
            ),
            reason="Sunucu kurulumu"
        )
        
        # Üye rolü (temel yetkiler)
        uye_role = await guild.create_role(
            name="Üye",
            permissions=discord.Permissions(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),
            reason="Sunucu kurulumu"
        )
        
        # Komutu çalıştıran kullanıcıya admin rolü ver
        await interaction.user.add_roles(admin_role)
        
        # Kategorileri oluştur
        genel_category = await guild.create_category("GENEL", position=0)
        ses_category = await guild.create_category("SES KANALLARI", position=1)
        admin_category = await guild.create_category("ADMIN", position=2)

        # Kanal izinlerini ayarla
        # Genel kategori izinleri
        await genel_category.set_permissions(guild.default_role, view_channel=True)
        await genel_category.set_permissions(uye_role, view_channel=True)
        await genel_category.set_permissions(admin_role, manage_channels=True)
        await genel_category.set_permissions(mod_role, manage_channels=True)

        # Admin kategori izinleri
        await admin_category.set_permissions(guild.default_role, view_channel=False)
        await admin_category.set_permissions(uye_role, view_channel=False)
        await admin_category.set_permissions(admin_role, view_channel=True)
        await admin_category.set_permissions(mod_role, view_channel=True)

        # Ses kategorisi izinleri
        await ses_category.set_permissions(guild.default_role, view_channel=True)
        
        # Kanalları oluştur
        # GENEL KATEGORİSİ
        kurallar_channel = await genel_category.create_text_channel("📜-kurallar")
        duyuru_channel = await genel_category.create_text_channel("📢-duyurular")
        gelen_giden_channel = await genel_category.create_text_channel("👋-gelen-giden")
        sohbet_channel = await genel_category.create_text_channel("💬-sohbet")
        bot_komut_channel = await genel_category.create_text_channel("🤖-bot-komut")
        goruntulu_channel = await genel_category.create_text_channel("🖼️-görsel")
        
        # SES KATEGORİSİ
        ses1_channel = await ses_category.create_voice_channel("🔊 Ses 1")
        ses2_channel = await ses_category.create_voice_channel("🔊 Ses 2")
        ses3_channel = await ses_category.create_voice_channel("🔊 Ses 3")
        
        # ADMIN KATEGORİSİ
        admin_sohbet_channel = await admin_category.create_text_channel("💼-admin-sohbet")
        admin_log_channel = await admin_category.create_text_channel("📝-admin-log")
        
        # Kanal izinlerini özelleştir
        # Duyuru kanalı (sadece adminler yazabilir)
        await duyuru_channel.set_permissions(guild.default_role, send_messages=False)
        await duyuru_channel.set_permissions(admin_role, send_messages=True)
        await duyuru_channel.set_permissions(mod_role, send_messages=True)
        
        # Gelen-giden kanalı (sadece bot ve adminler yazabilir)
        await gelen_giden_channel.set_permissions(guild.default_role, send_messages=False)
        await gelen_giden_channel.set_permissions(admin_role, send_messages=True)
        await gelen_giden_channel.set_permissions(mod_role, send_messages=True)
        
        # Admin kanalları (sadece adminler görebilir)
        await admin_sohbet_channel.set_permissions(guild.default_role, view_channel=False)
        await admin_sohbet_channel.set_permissions(uye_role, view_channel=False)
        await admin_sohbet_channel.set_permissions(admin_role, view_channel=True)
        await admin_sohbet_channel.set_permissions(mod_role, view_channel=True)
        
        await admin_log_channel.set_permissions(guild.default_role, view_channel=False)
        await admin_log_channel.set_permissions(uye_role, view_channel=False)
        await admin_log_channel.set_permissions(admin_role, view_channel=True)
        await admin_log_channel.set_permissions(mod_role, view_channel=True)
        
        # Veritabanı ayarlarını güncelle
        set_autorole(guild.id, uye_role.id)
        set_log_channel(guild.id, gelen_giden_channel.id)
        
        # Kurulum tamamlandı mesajı
        embed = discord.Embed(
            title="✅ Sunucu Kurulumu Tamamlandı",
            description="Aşağıdaki yapılar başarıyla oluşturuldu:",
            color=discord.Color.green()
        )
        embed.add_field(name="Roller", value=f"{admin_role.mention}, {mod_role.mention}, {rehber_role.mention}, {uye_role.mention}", inline=False)
        embed.add_field(
            name="Kanallar", 
            value=(
                f"**Genel:** {kurallar_channel.mention}, {duyuru_channel.mention}, {gelen_giden_channel.mention}, {sohbet_channel.mention}, {bot_komut_channel.mention}, {goruntulu_channel.mention}\n"
                f"**Ses:** {ses1_channel.mention}, {ses2_channel.mention}, {ses3_channel.mention}\n"
                f"**Admin:** {admin_sohbet_channel.mention}, {admin_log_channel.mention}"
            ),
            inline=False
        )
        embed.add_field(name="Otorol", value=uye_role.mention, inline=False)
        embed.add_field(name="Log Kanalı", value=gelen_giden_channel.mention, inline=False)
        
        # Kurallar mesajı
        kurallar_embed = discord.Embed(
            title=f"📜 {guild.name} Sunucu Kuralları",
            description=(
                "1. Küfür, argo ve hakaret yasaktır. Her türlü aşağılayıcı, rahatsız edici veya kaba dil kullanımı, yazılı veya sesli iletişimde, profil isimlerinde ve avatarlarda yasaktır.\n"
                "2. Spam ve flood yapmak yasaktır. Aynı mesajı tekrar tekrar göndermek, gereksiz yere fazla mesaj atarak kanalları doldurmak veya anlamsız içerik paylaşmak yasaktır.\n"
                "3. Reklam ve özel bilgi paylaşımı yasaktır. Başka sunucuların, ürünlerin, hizmetlerin, sosyal medya hesaplarının veya kişisel bilgilerin (telefon numarası, adress vb.) paylaşılması yasaktır.\n"
                "4. Din, dil, ırk ayrımcılığı ve dini/milli değerlere hakaret yasaktır. Herhangi bir din, dil, ırk, etnik köken veya kültüre yönelik ayrımcı, aşağılayıcı veya hakaret içeren ifadeler kullanmak yasaktır.\n"
                "5. Yetkili talimatlarına uyma zorunluluğu. Sunucu yetkililerinin verdiği talimatlare uymak zorunludur. Yetkililere karşı saygısız veya karşı gelen davranışlar, uyarı veya ceza ile sonuçlanabilir.\n"
                "6. Kışkırtıcı ve tartışma çıkarma yasaktır. Sunucuda gereksiz yere tartışma başlatmak, üyeleri kışkırtmak veya huzursuzluğa neden olacak davranışlarda bulunmak yasaktır.\n"
                "7. Uygunsuz içerik paylaşımı yasaktır. Şiddet, müstehcenlik, yasa dışı faaliyetler veya rahatsız edici görseller içeren herhangi bir içerik paylaşmak yasaktır.\n"
                "8. Bot komutlarını yanlış kullanma yasaktır. Sunucudaki botların komutlarını kötüye kullanmak, spam yapmak veya botları aksatacak şekilde kullanmak yasaktır.\n\n"
                "Kurallara uymayanlar uyarılır veya direkt işlem uygulanır."
            ),
            color=0xFF0000
        )
        
        await interaction.followup.send(embed=embed)
        await kurallar_channel.send(embed=kurallar_embed)
    except Exception as e:
        await interaction.followup.send(f"Kurulum sırasında hata oluştu: {e}")
        print(f"{Fore.RED}Sunucu-kur komutu hatası: {e}{Style.RESET_ALL}")

# --- Yeni Komutlar: Yardım, Yetkilerim, Zar ---
@tree.command(name="yardim", description="Tüm komutlar ve kısa açıklamaları")
async def yardim(interaction: discord.Interaction):
    try:
        embed = discord.Embed(
            title="📖 Yardım Menüsü",
            description="Aşağıda kullanabileceğiniz tüm komutlar listelenmiştir:",
            color=discord.Color.blurple(),
            timestamp=datetime.now(timezone.utc)
        )
        
        # Mod Komutları
        mod_commands = (
            "`/logkanal` - Log kanalı ayarla\n"
            "`/uyarilar` - Kullanıcı uyarılarını göster\n"
            "`/warn` - Manuel uyarı ver\n"
            "`/uyarisil` - Uyarı sil\n"
            "`/clear` - Mesajları temizle\n"
            "`/mute` - Kullanıcıyı sustur\n"
            "`/unmute` - Susturmayı kaldır\n"
            "`/ban` - Kullanıcıyı banla\n"
            "`/op` - Korumalardan muaf tut\n"
            "`/unop` - Muafiyeti kaldır\n"
            "`/logs` - Mesaj loglarını göster\n"
        )
        
        # Genel Komutlar
        genel_commands = (
            "`/ping` - Bot gecikmesini göster\n"
            "`/avatar` - Avatar göster\n"
            "`/kullanici` - Kullanıcı bilgileri\n"
            "`/sunucu` - Sunucu bilgileri\n"
            "`/otorol` - Otorol ayarla\n"
            "`/sarki` - Şarkı öner\n"
            "`/afk` - AFK moduna geç\n"
            "`/oylama` - Oylama başlat\n"
            "`/oneri` - Öneri gönder\n"
            "`/level` - Level bilgisi\n"
        )
        
        # Sistem Komutları
        sistem_commands = (
            "`/levelsistemi` - Level sistemini ayarla\n"
            "`/language` - Dil rol sistemini ayarla\n"
            "`/sunucu-kur` - Sunucu kurulumu yap\n"
            "`/history` - Mod geçmişi\n"
            "`/oneriler` - Önerileri listele\n"
        )
        
        # Yeni Eklenenler
        yeni_commands = (
            "`/yetkilerim` - Yetkilerinizi göster\n"
            "`/zar` - Zar at\n"
        )
        
        embed.add_field(name="🔧 Mod Komutları", value=mod_commands, inline=False)
        embed.add_field(name="🔍 Genel Komutlar", value=genel_commands, inline=False)
        embed.add_field(name="⚙️ Sistem Komutları", value=sistem_commands, inline=False)
        embed.add_field(name="✨ Yeni Komutlar", value=yeni_commands, inline=False)
        embed.set_footer(text=f"Komut sayısı: {len(tree.get_commands())}")
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message("Yardım komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Yardım komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="yetkilerim", description="Sunucudaki yetkilerinizi gösterir")
async def yetkilerim(interaction: discord.Interaction):
    try:
        permissions = interaction.user.guild_permissions
        perms_list = [
            ("Yönetici", permissions.administrator),
            ("Mesaj Yönet", permissions.manage_messages),
            ("Kanal Yönet", permissions.manage_channels),
            ("Üyeleri Yönet", permissions.moderate_members),
            ("Rolleri Yönet", permissions.manage_roles),
            ("Ban Yetkisi", permissions.ban_members),
            ("Kick Yetkisi", permissions.kick_members),
            ("Susturma Yetkisi", permissions.moderate_members),
            ("Sunucuyu Yönet", permissions.manage_guild),
            ("Embed Linkler", permissions.embed_links),
            ("Dosya Yükle", permissions.attach_files),
            ("Tepki Ekle", permissions.add_reactions),
            ("Mention", permissions.mention_everyone),
            ("Webhook Yönet", permissions.manage_webhooks)
        ]
        
        description = ""
        for perm, has_perm in perms_list:
            description += f"{'✅' if has_perm else '❌'} {perm}\n"
        
        embed = discord.Embed(
            title="🔑 Yetkilerin",
            description=description,
            color=discord.Color.gold(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"{interaction.user} | Yetki Kontrolü")
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message("Yetkilerim komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Yetkilerim komutu hatası: {e}{Style.RESET_ALL}")

@tree.command(name="zar", description="1 ile belirtilen üst sınır arasında zar atar")
@app_commands.describe(ust_sinir="Zarın üst sınırı (varsayılan: 6)")
async def zar(interaction: discord.Interaction, ust_sinir: int = 6):
    try:
        if ust_sinir < 2:
            await interaction.response.send_message("Üst sınır en az 2 olmalıdır!", ephemeral=True)
            return
        
        result = random.randint(1, ust_sinir)
        
        embed = discord.Embed(
            title="🎲 Zar Sonucu",
            description=f"**{result}** (1-{ust_sinir})",
            color=discord.Color.green(),
            timestamp=datetime.now(timezone.utc)
        )
        
        if result == ust_sinir:
            embed.set_footer(text="🎉 Tam isabet!")
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message("Zar komutunda hata oluştu.", ephemeral=True)
        print(f"{Fore.RED}Zar komutu hatası: {e}{Style.RESET_ALL}")

# --- Botu Başlat ---
try:
    bot.run(token)
except Exception as e:
    print(f"{Fore.RED}Bot başlatma hatası: {e}{Style.RESET_ALL}")
