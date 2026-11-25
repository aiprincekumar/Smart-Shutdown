# -*- coding: utf-8 -*-
"""
gui.components.app_catalog: Windows application catalog definitions, display metadata,
and semantic categorization for Tab 5 SettingsView.
Department 05 Frontend & Desktop Engineering Compliant (Rule 28 < 200 lines).
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

from typing import List, Tuple, Dict

# Category tuple: (category_id, display_label, list_of_app_keys)
APP_CATEGORIES: List[Tuple[str, str, List[str]]] = [
    ("developer", "🛠️ Developer & IDEs", [
        "AntiGravity", "Visual Studio Code", "JetBrains IDEs", "Sublime Text", "Postman",
        "GitHub Desktop", "GitKraken", "Docker Desktop"
    ]),
    ("browsers", "🌐 Web Browsers", [
        "Google Chrome", "Microsoft Edge", "Mozilla Firefox", "Brave Browser", "Opera Browser"
    ]),
    ("office", "📊 Office & Productivity", [
        "Microsoft Word", "Microsoft Excel", "Microsoft PowerPoint", "Microsoft Outlook", "Notepad",
        "Adobe Acrobat Reader"
    ]),
    ("communication", "💬 Chat & Meetings", [
        "Slack / Discord", "Telegram", "WhatsApp", "Zoom", "Microsoft Teams"
    ]),
    ("media_gaming", "🎮 Media & Gaming", [
        "VLC Media Player", "Spotify", "Steam", "Epic Games", "OBS Studio"
    ]),
    ("system", "⚙️ System & Utilities", [
        "Windows Terminal", "Command Prompt / PowerShell", "7-Zip", "WinRAR"
    ]),
]

APP_DISPLAY_INFO: Dict[str, Tuple[str, str, str]] = {
    # Developer & IDEs
    "AntiGravity": ("AntiGravity IDE / Agent", "Terminate active AI agent processes on shutdown.", "antigravity ide agent python process ai"),
    "Visual Studio Code": ("Visual Studio Code / Cursor", "Close VS Code and Cursor editor windows.", "visual studio code vscode cursor editor development"),
    "JetBrains IDEs": ("JetBrains IDEs", "Close IntelliJ IDEA, PyCharm, and Rider windows.", "jetbrains intellij idea pycharm rider ide dev"),
    "Sublime Text": ("Sublime Text", "Close Sublime Text code editor windows.", "sublime text editor code dev"),
    "Postman": ("Postman API Platform", "Close Postman API client windows on shutdown.", "postman api http rest client"),
    "GitHub Desktop": ("GitHub Desktop", "Close GitHub Desktop Git GUI client windows.", "github desktop git version control gui repository"),
    "GitKraken": ("GitKraken Git Client", "Close GitKraken desktop Git client windows.", "gitkraken git client version control repo"),
    "Docker Desktop": ("Docker Desktop", "Close Docker Desktop container management windows.", "docker desktop container kubernetes backend daemon"),

    # Web Browsers
    "Google Chrome": ("Google Chrome", "Close Google Chrome browser windows and tabs.", "google chrome browser web internet tabs"),
    "Microsoft Edge": ("Microsoft Edge", "Close Microsoft Edge browser windows and tabs.", "microsoft edge browser web internet tabs"),
    "Mozilla Firefox": ("Mozilla Firefox", "Close Mozilla Firefox browser windows and tabs.", "mozilla firefox browser web internet tabs"),
    "Brave Browser": ("Brave Browser", "Close Brave private browser windows and tabs.", "brave browser web internet tabs shields privacy"),
    "Opera Browser": ("Opera / Opera GX", "Close Opera and Opera GX gaming browser windows.", "opera opera-gx browser web internet gaming tabs"),

    # Office & Productivity
    "Microsoft Word": ("Microsoft Word", "Close Microsoft Word documents on shutdown.", "microsoft word winword doc docx office"),
    "Microsoft Excel": ("Microsoft Excel", "Close Microsoft Excel spreadsheets on shutdown.", "microsoft excel xls xlsx spreadsheet office"),
    "Microsoft PowerPoint": ("Microsoft PowerPoint", "Close Microsoft PowerPoint presentations.", "microsoft powerpoint powerpnt ppt pptx office"),
    "Microsoft Outlook": ("Microsoft Outlook", "Close Microsoft Outlook email and calendar windows.", "microsoft outlook email mail office"),
    "Notepad": ("Notepad & Text Editors", "Close Notepad, Notepad++, and basic text editors.", "notepad notepad++ editor text notes wordpad"),
    "Adobe Acrobat Reader": ("Adobe Acrobat Reader", "Close Adobe Acrobat and PDF reader documents.", "adobe acrobat reader pdf document viewer acrord32"),

    # Chat & Meetings
    "Slack / Discord": ("Slack & Discord", "Close Slack, Discord, and community messaging apps.", "slack discord chat messaging communication team"),
    "Telegram": ("Telegram Desktop", "Close Telegram desktop messaging windows.", "telegram chat messaging social"),
    "WhatsApp": ("WhatsApp Desktop", "Close WhatsApp desktop messaging windows.", "whatsapp chat messaging social"),
    "Zoom": ("Zoom Meetings", "Close Zoom video conferencing and meeting windows.", "zoom meeting video conference call"),
    "Microsoft Teams": ("Microsoft Teams", "Close Microsoft Teams meeting and chat windows.", "teams microsoft chat meeting call office"),

    # Media & Gaming
    "VLC Media Player": ("VLC Media Player", "Close VLC media playback windows on shutdown.", "vlc media player video audio movie"),
    "Spotify": ("Spotify Music", "Close Spotify desktop music player on shutdown.", "spotify music audio songs player stream"),
    "Steam": ("Steam Client", "Close Steam gaming client and games on shutdown.", "steam games gaming valve store"),
    "Epic Games": ("Epic Games Launcher", "Close Epic Games launcher and active titles.", "epic games launcher unreal store"),
    "OBS Studio": ("OBS Studio", "Close OBS Studio streaming and recording software.", "obs studio streaming recording broadcast video obs64"),

    # System & Utilities
    "Windows Terminal": ("Windows Terminal", "Close Windows Terminal tabs and windows.", "windows terminal wt console cli tab"),
    "Command Prompt / PowerShell": ("Command Prompt / PowerShell", "Close Command Prompt, PowerShell, and Git Bash.", "command prompt powershell cmd pwsh bash git-bash console"),
    "7-Zip": ("7-Zip File Manager", "Close 7-Zip archive and file manager windows.", "7zip 7-zip 7z archive file manager compression"),
    "WinRAR": ("WinRAR Archiver", "Close WinRAR compression and archive manager windows.", "winrar rar zip archive compression manager"),
}
