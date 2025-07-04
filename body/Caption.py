import re
import asyncio
from pyrogram import *
from html import unescape
from info import *
from Script import script
from .database import *
from pyrogram.errors import FloodWait
from pyrogram.types import *

# Yeh function pehle kahin pe hona chahiye file me
FONT_MAP = {
    "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ꜰ", "g": "ɢ",
    "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ",
    "o": "ᴏ", "p": "ᴘ", "q": "ǫ", "r": "ʀ", "s": "ꜱ", "t": "ᴛ", "u": "ᴜ",
    "v": "ᴠ", "w": "ᴡ", "x": "x", "y": "ʏ", "z": "ᴢ",    
    "A": "ᴀ", "B": "ʙ", "C": "ᴄ", "D": "ᴅ", "E": "ᴇ", "F": "ꜰ", "G": "ɢ",
    "H": "ʜ", "I": "ɪ", "J": "ᴊ", "K": "ᴋ", "L": "ʟ", "M": "ᴍ", "N": "ɴ",
    "O": "ᴏ", "P": "ᴘ", "Q": "ǫ", "R": "ʀ", "S": "ꜱ", "T": "ᴛ", "U": "ᴜ",
    "V": "ᴠ", "W": "ᴡ", "X": "x", "Y": "ʏ", "Z": "ᴢ",    
    "0": "𝟶", "1": "𝟷", "2": "𝟸", "3": "𝟹", "4": "𝟺",
    "5": "𝟻", "6": "𝟼", "7": "𝟽", "8": "𝟾", "9": "𝟿"
}

def convert_font(text: str) -> str:
    return ''.join(FONT_MAP.get(char, char) for char in text)
    
@Client.on_callback_query(filters.regex(r'^start'))
async def start(bot, query):
    await query.message.edit_text(
        text=script.START_TXT.format(query.from_user.mention),  
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("➕️ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ➕️", url=f"http://t.me/CustomCaptionBot?startchannel=true")
                ],[
                InlineKeyboardButton("Hᴇʟᴘ", callback_data="help"),
                InlineKeyboardButton("Aʙᴏᴜᴛ", callback_data="about")
            ],[
                InlineKeyboardButton("🌐 Uᴘᴅᴀᴛᴇ", url=f"https://t.me/Silicon_Bot_Update"),
                InlineKeyboardButton("📜 Sᴜᴘᴘᴏʀᴛ", url=r"https://t.me/Silicon_Botz")
            ]]
        ),
        disable_web_page_preview=True
)

@Client.on_callback_query(filters.regex(r'^help'))
async def help(bot, query):
    await query.message.edit_text(
        text=script.HELP_TXT,
        reply_markup=InlineKeyboardMarkup(
            [[
            InlineKeyboardButton('About', callback_data='about')
            ],[
            InlineKeyboardButton('↩ ʙᴀᴄᴋ', callback_data='start')
            ]]
        ),
        disable_web_page_preview=True    
)

@Client.on_callback_query(filters.regex(r'^about'))
async def about(bot, query):
    await query.message.edit_text(
        text=script.ABOUT_TXT,
        reply_markup=InlineKeyboardMarkup(
            [[
            InlineKeyboardButton('ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ ❓', callback_data='help')
            ],[
            InlineKeyboardButton('↩ ʙᴀᴄᴋ', callback_data='start')
            ]]
        ),
        disable_web_page_preview=True 

)

@Client.on_message(filters.command("set_cap") & filters.channel)
async def setCap(bot, message):
    if len(message.command) < 2:
        return await message.reply(
            "Usᴀɢᴇ: **/set_cap Your Caption**\n\n"
            "You can use dynamic placeholders like:\n"
            "`{file_name}`, `{file_size}`, `{languages}`, `{year}` etc.\n\n"
            "Type /formats for full list."
        )
    chnl_id = message.chat.id
    caption = message.text.split(" ", 1)[1]
    chkData = await chnl_ids.find_one({"chnl_id": chnl_id})
    if chkData:
        await updateCap(chnl_id, caption)
    else:
        await addCap(chnl_id, caption)
    await message.reply(f"✅ 𝐍𝐞𝐰 𝐂𝐚𝐩𝐭𝐢𝐨𝐧 𝐒𝐚𝐯𝐞𝐝:\n\n{caption}")

# Caption Delete Command
@Client.on_message(filters.command("del_cap") & filters.channel)
async def delCap(_, msg):
    chnl_id = msg.chat.id
    try:
        await chnl_ids.delete_one({"chnl_id": chnl_id})
        await msg.reply("✅ 𝐂𝐚𝐩𝐭𝐢𝐨𝐧 𝐃𝐞𝐥𝐞𝐭𝐞𝐝. 𝐃𝐞𝐟𝐚𝐮𝐥𝐭 𝐅𝐨𝐫𝐦𝐚𝐭 𝐰𝐢𝐥𝐥 𝐛𝐞 𝐮𝐬𝐞𝐝.")
    except Exception as e:
        err = await msg.reply(f"Error: {e}")
        await asyncio.sleep(5)
        await err.delete()

# Broadcast Caption Apply
@Client.on_message(filters.channel)
async def reCap(bot, message):
    chnl_id = message.chat.id
    default_caption = message.caption or ""
    if message.media:
        for ftype in ("video", "audio", "document", "voice"):
            obj = getattr(message, ftype, None)
            if obj and hasattr(obj, "file_name"):
                file_info = extract_info(obj.file_name, obj.file_size, default_caption)
                cap_dets = await chnl_ids.find_one({"chnl_id": chnl_id})
                template = cap_dets["caption"] if cap_dets else DEF_CAP
                caption = parse_caption_format(template, file_info)
                try:
                    await message.edit(caption)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                except Exception:
                    pass
    return

# Caption Format Parser
def parse_caption_format(template: str, file_info: dict) -> str:
    return template.format(
        gk=file_info.get("gk", ""),
        file_name=file_info.get("file_name", ""),
        file_size=file_info.get("file_size", ""),
        file_caption=file_info.get("file_caption", ""),
        languages=file_info.get("languages", ""),
        subtitles=file_info.get("subtitles", ""),
        duration=file_info.get("duration", ""),
        ott=file_info.get("ott", ""),
        title=file_info.get("title", ""),
        resolution=file_info.get("resolution", ""),
        name=file_info.get("name", ""),
        year=file_info.get("year", ""),
        quality=file_info.get("quality", ""),
        lanaudio=file_info.get("lanaudio", ""),
        season=file_info.get("season", ""),
        episode=file_info.get("episode", ""),
        audio=file_info.get("audio", ""),
        lib=file_info.get("lib", ""),
        extension=file_info.get("extension", ""),
        shortsub=file_info.get("shortsub", "")
    )

# Extract Meta Info from File Name
def extract_info(file_name: str, file_size: int, default_caption: str) -> dict:
    name = re.sub(r"[@._]", " ", file_name).strip()
    return {
        "file_name": file_name,
        "file_size": get_size(file_size),
        "file_caption": default_caption,
        "languages": extract_language(default_caption),
        "subtitles": extract_subtitles(default_caption),
        "duration": "00:00:00",  # TODO: Add actual duration if available
        "ott": extract_ott(default_caption),
        "title": extract_title_only(file_name),
        "resolution": extract_resolution(default_caption),
        "name": extract_clean_title(default_caption),
        "year": extract_year(default_caption),
        "quality": extract_quality(default_caption),
        "lanaudio": extract_lanaudio(default_caption),
        "season": extract_season(default_caption),
        "episode": extract_episode(default_caption),
        "audio": extract_audio(default_caption),
        "lib": extract_lib(default_caption),
        "extension": extract_extension(default_caption),
        "shortsub": extract_shortsub(default_caption),
    }

# All Helper Extractors
def extract_language(text):
    if not text:
        return convert_font("ORG Language")

    # Clean formatting & normalize
    text = unescape(text)
    text = re.sub(r'</?(b|i|u|strong|em|code|a)( [^>]*)?>', '', text, flags=re.IGNORECASE)
    text = text.replace("_", " ").replace(".", " ").replace("-", " ")

    # Lowercase version for matching
    lower_text = text.lower()

    # Language mapping
    lang_map = {
        "hindi": "Hindi", "hin": "Hindi", "hi": "Hindi",
        "english": "English", "eng": "English", "en": "English",
        "tamil": "Tamil", "tam": "Tamil", "ta": "Tamil",
        "telugu": "Telugu", "tel": "Telugu", "te": "Telugu",
        "malayalam": "Malayalam", "mal": "Malayalam", "ml": "Malayalam",
        "kannada": "Kannada", "kan": "Kannada", "kn": "Kannada",
        "bengali": "Bengali", "ben": "Bengali", "bn": "Bengali",
        "marathi": "Marathi", "mar": "Marathi", "mr": "Marathi",
        "punjabi": "Punjabi", "pan": "Punjabi", "pa": "Punjabi",
        "gujarati": "Gujarati", "guj": "Gujarati", "gu": "Gujarati",
        "urdu": "Urdu", "urd": "Urdu", "ur": "Urdu",
        "korean": "Korean", "kor": "Korean", "ko": "Korean",
        "japanese": "Japanese", "jap": "Japanese", "ja": "Japanese",
        "chinese": "Chinese", "chi": "Chinese", "zh": "Chinese",
        "french": "French", "fre": "French", "fr": "French",
        "german": "German", "ger": "German", "de": "German",
        "arabic": "Arabic", "ara": "Arabic", "ar": "Arabic",
        "thai": "Thai", "th": "Thai",
        "indonesian": "Indonesian", "indo": "Indonesian", "id": "Indonesian"
    }

    found = set()
    for key, full in lang_map.items():
        if re.search(rf'\b{re.escape(key)}\b', lower_text):
            found.add(full)

    return convert_font(" ".join(sorted(found))) if found else convert_font("ORG Language")

def extract_lanaudio(text):
    if not text:
        return convert_font("ORG Language")

    # --- Clean formatting ---
    text = unescape(text)
    text = re.sub(r'</?(b|i|u|strong|em|code|a)( [^>]*)?>', '', text, flags=re.IGNORECASE)
    text = text.replace("_", " ").replace(".", " ").replace("-", " ")

    # Lowercase version for detection
    lower_text = text.lower()

    # --- Language keywords ---
    lang_keywords = {
        "hindi": "Hindi", "hin": "Hindi", "hi": "Hindi",
        "english": "English", "eng": "English", "en": "English",
        "tamil": "Tamil", "tam": "Tamil", "ta": "Tamil",
        "telugu": "Telugu", "tel": "Telugu", "te": "Telugu",
        "malayalam": "Malayalam", "mal": "Malayalam", "ml": "Malayalam",
        "kannada": "Kannada", "kan": "Kannada", "kn": "Kannada",
        "bengali": "Bengali", "ben": "Bengali", "bn": "Bengali",
        "marathi": "Marathi", "mar": "Marathi", "mr": "Marathi",
        "punjabi": "Punjabi", "pan": "Punjabi", "pa": "Punjabi",
        "gujarati": "Gujarati", "guj": "Gujarati", "gu": "Gujarati",
        "urdu": "Urdu", "urd": "Urdu", "ur": "Urdu",
        "korean": "Korean", "kor": "Korean", "ko": "Korean",
        "japanese": "Japanese", "jap": "Japanese", "ja": "Japanese",
        "chinese": "Chinese", "chi": "Chinese", "zh": "Chinese",
        "french": "French", "fre": "French", "fr": "French",
        "german": "German", "ger": "German", "de": "German",
        "arabic": "Arabic", "ara": "Arabic", "ar": "Arabic",
        "thai": "Thai", "th": "Thai",
        "indonesian": "Indonesian", "indo": "Indonesian", "id": "Indonesian"
    }

    # --- Audio format keywords ---
    audio_keywords = [
        # Common formats
        "aac", "aac2.0", "aac5.1", "aac7.1", "aac lc", "aac lc2.0", "aac lc5.1",
        "mp3", "ogg", "flac", "opus", "pcm", "alac", "wma", "mka",

        # Dolby & DTS
        "dd", "dd+", "ddp", "dd2.0", "dd5.1", "dd7.1", "ddp2.0", "ddp5.1", "ddp7.1",
        "eac3", "ac3", "ac-3", "truehd", "truehd atmos", "atmos", "dolby", "dolby atmos", "dolbyaudio",
        "dts", "dts-hd", "dts:x", "dts:x", "dtsma", "dts-hdma", "dts express", "dts es",

        # Channel formats
        "5.1", "7.1", "9.1", "11.1", "2.0", "2ch", "6ch", "1ch", "mono", "stereo",

        # Recording type
        "line audio", "cam audio", "clean audio", "original audio", "org audio", "studio audio", "theatrical audio",

        # Label/misc
        "dual audio", "multi audio", "dual", "multi", "director's commentary", "commentary",

        # Bitrates
        "64kbps", "96kbps", "112kbps", "128kbps", "160kbps", "192kbps", "224kbps",
        "256kbps", "320kbps", "384kbps", "448kbps", "512kbps", "640kbps", "768kbps",
        "896kbps", "1024kbps", "1509kbps", "1536kbps", "1920kbps", "2048kbps",

        # Noise/distortion tags
        "hall audio", "mic audio", "ts audio", "tcam", "vhsrip audio"
    ]

# --- Step 1: Split by '+' first ---
    parts = re.split(r'\s*\+\s*', lower_text)

    lang_audio_pairs = []
    audio_format_buffer = None

    bitrate_pattern = r"(~?\s*\d{2,4}\s?kbps)"

    for part in parts:
        langs_found = []
        audio_found = []
        bitrate_found = []

        # Language detection
        for lang in lang_keywords:
            if re.search(rf'\b{re.escape(lang)}\b', part):
                langs_found.append(lang.title())

        # Audio format detection
        for audio in audio_keywords:
            if re.search(rf'\b{re.escape(audio)}\b', part):
                audio_found.append(audio.upper() if not any(x.isupper() for x in audio) else audio)

        # Bitrate detection
        for br in re.findall(bitrate_pattern, part):
            clean = re.sub(r"\s+", "", br).upper()
            if not clean.endswith("KBPS"):
                clean += "KBPS"
            if not clean.startswith("~"):
                clean = "~" + clean
            bitrate_found.append(clean)

        # Attach bitrate to last audio
        if audio_found and bitrate_found:
            audio_found[-1] = f"{audio_found[-1]} {bitrate_found[-1]}"
        elif not audio_found and bitrate_found:
            audio_found.append(bitrate_found[-1])

        if not audio_found and audio_format_buffer:
            lang_audio_pairs.append((langs_found, [audio_format_buffer]))
        elif langs_found or audio_found:
            lang_audio_pairs.append((langs_found, audio_found))
            if audio_found:
                audio_format_buffer = audio_found[-1]

    # Feature 4: Handle "Dual Audio"/"Multi Audio"
    if "dual audio" in lower_text or "multi audio" in lower_text:
        dual_langs = []
        for lang in lang_keywords:
            if re.search(rf'\b{re.escape(lang)}\b', lower_text):
                dual_langs.append(lang.title())
        if dual_langs:
            dual_audio = audio_format_buffer or ""
            lang_audio_pairs = [(dual_langs, [dual_audio])] if dual_audio else [(dual_langs, [])]

    # Final output — skip extra space if no audio
    result = []
    for langs, audios in lang_audio_pairs:
        if not langs and not audios:
            continue
        if langs:
            for i, lang in enumerate(langs):
                audio = audios[i] if audios and i < len(audios) else (audios[-1] if audios else "")
                if audio:
                    result.append(f"{lang} {audio}")
                else:
                    result.append(f"{lang}")
        elif audios:
            result.append(" + ".join(audios))

    return convert_font(" + ".join(result)) if result else convert_font("ORG Language")

def extract_subtitles(text):
    if not text:
        return convert_font("")

    # Clean formatting
    text = unescape(text)
    text = re.sub(r"</?(b|i|u|strong|em|code|a)( [^>]*)?>", "", text, flags=re.IGNORECASE)
    text = text.replace("_", " ").replace(".", " ").replace("-", " ")

    # Prepare subtitle types (original format)
    subtitle_tags = [
        "ESub", "MSub", "HSub", "PSUB", "SSUB", "NSUB",
        "ForcedSub", "FanSub", "DualSub", "MultiSub",
        "SoftSub", "HardSub", "Subbed", "Subs", "Subtitles",
        "EngSub", "HinSub", "NoSub", "EmbeddedSubs",
        "BurnedSub", "RetailSub",
        "English Sub", "Hindi Sub", "English Subtitle", "Hindi Subtitle",
        "Tamil Sub", "Telugu Sub", "Bangla Sub", "Bengali Sub", "Malayalam Sub",
        "Arabic Sub", "Persian Sub", "Urdu Sub", "French Sub", "German Sub", "Korean Sub",
        "Japanese Sub", "Chinese Sub", "Indonesian Sub", "Thai Sub", "Marathi Sub",
        "EnglishSubs", "HindiSubs", "TamilSubs", "TeluguSubs", "BanglaSubs"
    ]

    # Collect all matches (case-insensitive but preserve original tag)
    found = []
    lowered_text = text.lower()
    for tag in subtitle_tags:
        if tag.lower() in lowered_text and tag not in found:
            found.append(tag)

    return convert_font(", ".join(found)) if found else convert_font("")


def extract_year(text):
    if not text:
        return convert_font("")

    # Remove Telegram/HTML formatting
    text = unescape(text)
    text = re.sub(r'</?(b|i|u|strong|em|code|a)( [^>]*)?>', '', text, flags=re.IGNORECASE)
    text = text.replace("_", " ").replace(".", " ").replace("-", " ")

    # Match valid years from 1900 to 2099
    match = re.search(r'\b(19\d{2}|20\d{2})\b', text)
    return match.group(1) if match else convert_font("")

def extract_ott(text):
    if not text:
        return convert_font("")

    # Clean formatting
    text = unescape(text)
    text = re.sub(r'</?(b|i|u|strong|em|code|a)( [^>]*)?>', '', text, flags=re.IGNORECASE)
    text = text.replace("_", " ").replace(".", " ").replace("-", " ")

    # Convert to lowercase for case-insensitive matching
    lowered_text = text.lower()

    # OTT platform tags and aliases (all in lowercase)
    ott_tags = {
        "nf": ["nf", "netflix"],
        "amzn": ["amzn", "amazon", "primevideo", "prime", "amazonprime"],
        "dsny": ["dsny", "disney", "hotstar", "disneyplus", "disney+hotstar", "dsnp"],
        "hbo": ["hbo", "hmax", "hbo max", "max"],
        "apl": ["apl", "apple", "appletv", "appletv+"],
        "mx": ["mx", "mxplayer"],
        "alt": ["alt", "altbalaji"],
        "zee5": ["zee5", "zee"],
        "jio": ["jio", "jiocinema"],
        "sony": ["sony", "sonyliv", "liv"],
        "voot": ["voot"],
        "hulu": ["hulu"],
        "paramount": ["paramount", "paramountplus", "paramount+"],
        "lionsgate": ["lionsgate", "lionsgateplay"]
    }

    for tag, aliases in ott_tags.items():
        for alias in aliases:
            if re.search(rf'\b{re.escape(alias)}\b', lowered_text):
                return convert_font(tag)

    return convert_font("")

def extract_resolution(text):
    if not text:
        return convert_font("")

    # Clean formatting
    text = unescape(text)
    text = re.sub(r'</?(b|i|u|strong|em|code|a)( [^>]*)?>', '', text, flags=re.IGNORECASE)
    cleaned_text = text.replace("_", " ").replace(".", " ").replace("-", " ").lower()

    # Resolution keywords
    resolution_tags = {
        "2160p": "2160p", "4k": "4K",
        "1440p": "1440p",
        "1080p": "1080p",
        "960p": "960p",
        "720p": "720p", "hd": "HD",
        "576p": "576p", "540p": "540p", "480p": "480p",
        "360p": "360p", "240p": "240p", "144p": "144p", "ld": "LD"
    }

    resolution_found = ""
    for keyword, display in resolution_tags.items():
        if re.search(rf'\b{re.escape(keyword)}\b', cleaned_text):
            resolution_found = display
            break

    if not resolution_found:
        return convert_font("")

    # Check for 10bit
    has_10bit = re.search(r'\b10\s?bit\b', cleaned_text)

    # Check for HEVC only (ignore x265 completely)
    has_hevc = re.search(r'\bhevc\b', cleaned_text)

    # Build result
    parts = [resolution_found]
    if has_10bit:
        parts.append("10bit")
    if has_hevc:
        parts.append("HEVC")

    return convert_font(" ".join(parts))
    
def extract_quality(text):
    if not text:
        return convert_font("")

    # Clean formatting (Telegram/HTML safe)
    text = unescape(text)
    text = re.sub(r'</?(b|i|u|strong|em|code|a)( [^>]*)?>', '', text, flags=re.IGNORECASE)
    text = text.replace("_", " ").replace(".", " ").replace("-", " ")

    # All common + rare + OTT/fan tags
    quality_tags = [
        "WEB DL", "WEBRip", "WEB", "WEBDL", "WBDL", "WEBHD",           # Web variants
        "BluRay", "BRRip", "BDRip", "BDRemux",                         # BluRay
        "HDRip", "HDTV", "HDTVRip", "HDT",                             # TV Rip
        "DVDRip", "PDVDRip", "PreDVD", "DVDScr", "DVD",               # DVD
        "SATRip", "TVRip", "VHSRip",                                   # Satellite / old rips
        "CAMRip", "HDCAM", "CAM", "TS", "HDTS", "R5",                  # Theater / Screener
        "HDR", "HDR10+", "Dolby Vision",                 # High dynamic range
        "FHD", "UHD",                                               # Resolution-based
        "SD", "HD", "HQ", "LQ",                                        # General Quality
        "Proper", "Repack", "Remux", "Encode",                         # Scene tags
        "Original Print",                                              # OTT Print
        "Untouched", "Uncompressed",                                   # Pure Quality
        "DV", "IMAX", "Dolby ATMOS", "TrueHD",                         # Advanced terms
    ]

    for tag in quality_tags:
        if re.search(rf'\b{re.escape(tag)}\b', text, re.IGNORECASE):
            return convert_font(tag.upper())

    return convert_font("")
    
def extract_season(text):
    if not text:
        return convert_font("")

    # Clean HTML/Telegram formatting
    text = unescape(text)
    text = re.sub(r'</?(b|i|u|strong|em|code|a)( [^>]*)?>', '', text, flags=re.IGNORECASE)
    text = text.replace("_", " ").replace(".", " ").replace("-", " ")

    # All possible patterns for season
    patterns = [
        r'\bS(?:eason)?\s?(\d{1,2})\b',        # S01 or Season 1
        r'\b(\d{1,2})x\d{1,2}\b',              # 1x03 → Season 1
        r'\bPart\s?(\d{1,2})\b',               # Part 1 (some series use this)
        r'\bVol(?:ume)?\s?(\d{1,2})\b',        # Volume 1
        r'\bBook\s?(\d{1,2})\b',               # Book 2 (used in some anime)
        r'\b(\d{1,2})\sst\s?Season\b',         # 1st Season
    ]

    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            num = match.group(1).zfill(2)
            return convert_font(f"S{num}")

    return convert_font("")

def extract_episode(text):
    if not text:
        return convert_font("")

    # Clean text formatting
    text = unescape(text)
    text = re.sub(r'</?(b|i|u|strong|em|code|a)( [^>]*)?>', '', text, flags=re.IGNORECASE)
    text = text.replace("_", " ").replace(".", " ").replace("-", " ")

    # Try all common episode patterns
    patterns = [
        r'\bE[Pp]?\s?(\d{1,3})\b',          # E03 or Ep03 or EP 03
        r'\b(?:Episode|Ep)\s?(\d{1,3})\b',  # Episode 3, Ep3
        r'\bS\d{1,2}E(\d{1,3})\b',          # S01E03 → get 03
        r'\b(\d{1,3})\s?of\s?\d{1,3}\b',    # 3 of 10 (fallback)
        r'\bPart\s?(\d{1,3})\b',            # Part 3
    ]

    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            num = match.group(1).zfill(2)  # Pad with 0 if needed
            return convert_font(f"E{num}")

    return convert_font("")  # Default fallback

def extract_audio(text):
    if not text:
        return convert_font("")

    # Clean formatting
    text = unescape(text)
    text = re.sub(r'</?(b|i|u|strong|em|code|a)( [^>]*)?>', '', text, flags=re.IGNORECASE)
    cleaned_text = text.replace("_", " ").replace(".", " ").replace("-", " ").lower()

    # Extensive list of audio tags
    audio_tags = [
        "aac", "aac2.0", "aac5.1", "aac7.1",
        "ddp", "ddp2.0", "ddp5.1", "ddp7.1",
        "dd", "ddp", "dd+", "eac3", "ac3", "ac-3",
        "dts", "dts-hd", "dts:x", "dtsma", "dts-hdma",
        "5.1", "7.1", "2.0", "2ch", "6ch", "1ch", "9.1", "11.1",
        "stereo", "mono", "dual audio", "multi audio", "dual", "multi",
        "hindi audio", "hindi track", "org audio", "original audio",
        "eng audio", "clean audio", "line audio", "cam audio"
    ]

    found = []
    for tag in audio_tags:
        pattern = re.escape(tag)
        if re.search(rf'\b{pattern}\b', cleaned_text):
            if tag not in found:
                found.append(tag)

    # Capitalize appropriately
    formatted = [t.upper() if not any(x.isupper() for x in t) else t for t in found]
    return convert_font(", ".join(formatted)) if found else convert_font("")

def extract_lib(text):
    if not text:
        return convert_font("x264")

    # Decode HTML entities and remove Telegram formatting
    text = unescape(text)
    text = re.sub(r'</?(b|i|u|strong|em|code|a)( [^>]*)?>', '', text, flags=re.IGNORECASE)

    # Normalize separators
    text = text.replace("_", " ").replace(".", " ").replace("-", " ")

    # Define all common/rare codec libraries
    codec_tags = [
        "x264", "x265", "h264", "h265", "h.264", "h.265",
        "hevc", "av1", "vp9", "vp8", "divx", "mpeg4", "prores", "theora"
    ]

    for tag in codec_tags:
        if re.search(rf'\b{re.escape(tag)}\b', text, re.IGNORECASE):
            return convert_font(tag.lower())

    return convert_font("x264")  # Default fallback
    
def extract_shortsub(text):
    subtitle_tags = [
        "ESub", "MSub", "HSub", "PSUB", "SSUB", "NSUB", "ForcedSub",
        "Subbed", "Subs", "SoftSub", "HardSub", "DualSub", "MultiSub",
        "EngSub", "HinSub", "NoSub", "Subtitles", "EmbeddedSubs",
        "BurnedSub", "RetailSub", "FanSub"
    ]

    if not text:
        return convert_font("")

    # Decode HTML entities (for hyperlinks)
    text = unescape(text)

    # Remove Telegram formatting tags like <b>, <i>, <u>, <a>
    text = re.sub(r'</?(b|i|u|strong|em|code|a)( [^>]*)?>', '', text, flags=re.IGNORECASE)

    # Normalize separators: dot, underscore, dash → space
    text = text.replace(".", " ").replace("_", " ").replace("-", " ")

    # Remove markdown characters: *, _, ~, `
    text = re.sub(r'[*_~`]', '', text)

    # Actual matching
    for tag in subtitle_tags:
        if re.search(rf'\b{tag}\b', text, re.IGNORECASE):
            return convert_font(tag)

    return convert_font("")

def extract_extension(text):
    if not text:
        return convert_font(".mkv")

    # Clean formatting
    text = unescape(text)
    text = re.sub(r'</?(b|i|u|strong|em|code|a)( [^>]*)?>', '', text, flags=re.IGNORECASE)
    text = text.replace(" ", "").lower()

    # Known extensions
    extensions = [
        ".mkv", ".mp4", ".webm", ".avi", ".mov", ".flv", ".wmv", ".ts", ".m4v", ".mpeg", ".mpg",
        ".3gp", ".vob", ".ogv", ".rm", ".rmvb", ".asf", ".f4v", ".m2ts", ".mpe", ".divx", ".mxf"
    ]

    for ext in extensions:
        if ext in text:
            return convert_font(ext)

    return convert_font(".mkv")

def extract_title_only(text):
    if not text:
        return convert_font("Unknown Title")

    # Decode HTML entities & remove Telegram-style formatting
    text = unescape(text)
    text = re.sub(r'</?(b|i|u|strong|em|code|a)( [^>]*)?>', '', text, flags=re.IGNORECASE)

    # Normalize separators
    text = text.replace("_", " ").replace(".", " ").replace("-", " ")

    # Patterns to remove common junk
    patterns = [
        # Season / Episode
        r'\bS\d{1,2}E\d{1,2}\b', r'\bS\d{1,2}\b', r'\bE\d{1,2}\b',

        # Year
        r'\b(19|20)\d{2}\b',

        # Resolutions
        r'\b[23]60p\b', r'\b480p\b', r'\b576p\b', r'\b720p\b',
        r'\b1080p\b', r'\b2160p\b', r'\b4K\b', r'\b8K\b',

        # Print / Source
        r'\bWEB[- ]?DL\b', r'\bWEBRip\b', r'\bBluRay\b', r'\bBRRip\b',
        r'\bHDRip\b', r'\bDVDRip\b', r'\bHDTV\b', r'\bCAMRip\b',
        r'\bHDCAM\b', r'\bTS\b', r'\bPDVDRip\b', r'\bPreDVD\b', r'\bHDTS\b',

        # Quality
        r'\bHQ\b', r'\bLQ\b', r'\bFHD\b', r'\bUHD\b', r'\bSD\b', r'\bHD\b',

        # Audio
        r'\bAAC\b', r'\bDDP?\b', r'\bOGG\b', r'\bMP3\b', r'\bFLAC\b',
        r'\bTrueHD\b', r'\bATMOS\b',

        # Channels
        r'\b5\.1\b', r'\b7\.1\b', r'\b2\.0\b', r'\b6CH\b', r'\b2CH\b', r'\b1CH\b',

        # Subtitles
        r'\bESub\b', r'\bMSub\b', r'\bHSub\b', r'\bPSUB\b', r'\bSSUB\b',
        r'\bSoftSub\b', r'\bHardSub\b', r'\bSubbed\b', r'\bSubs\b', r'\bNSUB\b',

        # Codecs
        r'\bx264\b', r'\bx265\b', r'\bH\.264\b', r'\bHEVC\b', r'\bAV1\b', r'\bDivX\b',

        # OTT Platforms
        r'\bNF\b', r'\bNetflix\b', r'\bAMZN\b', r'\bAmazon\b', r'\bPrimeVideo\b',
        r'\bDSNY\b', r'\bDisney\b', r'\bHotstar\b', r'\bJio\b', r'\bJioCinema\b',
        r'\bZEE5\b', r'\bZee\b', r'\bALT\b', r'\bMx\b', r'\bSony\b', r'\bVoot\b',

        # Languages
        r'\bHindi\b', r'\bEnglish\b', r'\bTamil\b', r'\bTelugu\b',
        r'\bMalayalam\b', r'\bKannada\b', r'\bBengali\b', r'\bMarathi\b',
        r'\bPunjabi\b', r'\bKorean\b', r'\bJapanese\b', r'\bChinese\b',

        # File extensions
        r'\.mkv\b', r'\.mp4\b', r'\.webm\b', r'\.avi\b', r'\.mov\b',

        # Groups / tags / spam
        r'@[\w]+', r'#\w+', r't\.?me/\S+', r'www\.\S+',
        r'\bJoin\s+@?\w+\b', r'\bTG\b', r'\bGroup\b', r'\bTelegram\b',
        r'\bEncoded\b', r'By\s+\w+', r'\bEncode\b',

        # Extras
        r'\bUNCUT\b', r'\bORG\b', r'\bORIGINAL\b', r'\bREMASTERED\b',
        r'\bProper\b', r'\bRepack\b', r'\bDual\b', r'\bDubbed\b', r'\bFanDub\b',
        r'\bLine\b', r'\bExclusive\b', r'\bSample\b', r'\bRelease\b',

        # Extra symbols and brackets
        r'[©®™✓•☆★✦⟨⟩〈〉《》【】\{\}<>]', r'\s+'
    ]

    for pat in patterns:
        text = re.sub(pat, ' ', text, flags=re.IGNORECASE)

    # Final cleanup
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)

    clean_title = text.strip().title() or "Unknown Title"
    return convert_font(clean_title)
    
# Size Formatter
def get_size(size):
    units = ["Bytes", "Kʙ", "Mʙ", "Gʙ", "Tʙ"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units) - 1:
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

# Command to Show All Format Help
@Client.on_message(filters.command("formats") & filters.private)
async def show_formats(_, message):
    await message.reply_text("""
<b>📌 Aᴜᴛᴏ Rᴇɴᴀᴍᴇ Fᴏʀᴍᴀᴛs:</b>

<b>{file_name}</b> : Full file name  
<b>{file_size}</b> : File size like 2.45GB  
<b>{file_caption}</b> : Original file caption  
<b>{languages}</b> : Language(s) in media  
<b>{subtitles}</b> : Subtitles, like English  
<b>{duration}</b> : Duration (HH:MM:SS)  
<b>{ott}</b> : OTT platform (e.g., NF, AMZN)  
<b>{resolution}</b> : Resolution (e.g., 720p)  
<b>{name}</b> : Clean title (e.g., Premi Babu)  
<b>{year}</b> : Year (e.g., 2024)  
<b>{quality}</b> : Video quality (e.g., BluRay)  
<b>{season}</b> : Season (e.g., S01)  
<b>{episode}</b> : Episode (e.g., E03)  
<b>{audio}</b> : Audio type (e.g., AAC, 6CH)  
<b>{lib}</b> : Codec (e.g., x264, x265)  
<b>{extension}</b> : File extension (.mkv etc)  
<b>{shortsub}</b> : Subtitle tag (e.g., ESub)

<b>⚠️ Only HTML formatting is supported.</b>
""", disable_web_page_preview=True)

@Client.on_message(filters.command("start") & filters.private)
async def strtCap(bot, message):
    user_id = int(message.from_user.id)
    await insert(user_id)
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("➕️ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ➕️", url=f"https://t.me/CustomCaptionBot?startchannel=true")
            ],[
                InlineKeyboardButton("Hᴇʟᴘ", callback_data="help"),
                InlineKeyboardButton("Aʙᴏᴜᴛ", callback_data="about")
            ],[
                InlineKeyboardButton("🌐 Uᴘᴅᴀᴛᴇ", url=f"https://t.me/Silicon_Bot_Update"),
                InlineKeyboardButton("📜 Sᴜᴘᴘᴏʀᴛ", url=r"https://t.me/Silicon_Botz")
        ]]
    )
    await message.reply_photo(
        photo=SILICON_PIC,
        caption=f"<b>Hᴇʟʟᴏ {message.from_user.mention}\n\nɪ ᴀᴍ ᴀᴜᴛᴏ ᴄᴀᴘᴛɪᴏɴ ʙᴏᴛ ᴡɪᴛʜ ᴄᴜsᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ.\n\nFᴏʀ ᴍᴏʀᴇ ɪɴғᴏ ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ ᴄʟɪᴄᴋ ᴏɴ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ.\n\nMᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ »<a href='https://t.me/Silicon_Bot_Update'>Sɪʟɪᴄᴏɴ Bᴏᴛᴢ</a></b>",
        reply_markup=keyboard
    )

@Client.on_message(filters.private & filters.user(ADMIN)  & filters.command(["total_users"]))
async def all_db_users_here(client,message):
    silicon = await message.reply_text("Please Wait....")
    silicon_botz = await total_user()
    await silicon.edit(f"Tᴏᴛᴀʟ Usᴇʀ :- `{silicon_botz}`")

@Client.on_message(filters.private & filters.user(ADMIN) & filters.command(["broadcast"]))
async def broadcast(bot, message):
    if (message.reply_to_message):
        silicon = await message.reply_text("Geting All ids from database..\n Please wait")
        all_users = await getid()
        tot = await total_user()
        success = 0
        failed = 0
        deactivated = 0
        blocked = 0
        await silicon.edit(f"ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...")
        async for user in all_users:
            try:
                time.sleep(1)
                await message.reply_to_message.copy(user['_id'])
                success += 1
            except errors.InputUserDeactivated:
                deactivated +=1
                await delete({"_id": user['_id']})
            except errors.UserIsBlocked:
                blocked +=1
                await delete({"_id": user['_id']})
            except Exception as e:
                failed += 1
                await delete({"_id": user['_id']})
                pass
            try:
                await silicon.edit(f"<u>ʙʀᴏᴀᴅᴄᴀsᴛ ᴘʀᴏᴄᴇssɪɴɢ</u>\n\n• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {tot}\n• sᴜᴄᴄᴇssғᴜʟ: {success}\n• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}")
            except FloodWait as e:
                await asyncio.sleep(t.x)
        await silicon.edit(f"<u>ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</u>\n\n• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {tot}\n• sᴜᴄᴄᴇssғᴜʟ: {success}\n• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}")

