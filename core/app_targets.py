# -*- coding: utf-8 -*-
"""
core.app_targets: Critical OS whitelists, targeted apps, and process mapping tables.
Department 06 Backend & Systems Engineering / Department 02 Architecture Compliant.
Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
"""

from typing import Dict, Any

CRITICAL_OS_WHITELIST = {
    "system", "system idle process", "smss.exe", "csrss.exe", "wininit.exe",
    "services.exe", "lsass.exe", "winlogon.exe", "dwm.exe", "fontdrvhost.exe",
    "svchost.exe", "sihost.exe", "taskhostw.exe", "explorer.exe", "ctfmon.exe",
    "runtimebroker.exe", "shellexperiencehost.exe", "startmenuexperiencehost.exe",
    "searchhost.exe", "searchapp.exe", "searchui.exe", "textinputhost.exe",
    "securityhealthservice.exe", "securityhealthsystray.exe", "smartscreen.exe",
    "audiodg.exe", "spoolsv.exe", "dashost.exe", "dllhost.exe", "msmpeng.exe",
    "nissrv.exe", "registry", "memory compression", "wudfhost.exe", "lockapp.exe",
    "applicationframehost.exe", "systemsettings.exe", "phoneexperiencehost.exe",
    "igfxem.exe", "igfxtray.exe", "hkcmd.exe", "nvvsvc.exe",
    "nvdisplay.container.exe", "rtkngui64.exe", "ravbg64.exe", "conhost.exe",
}

TARGETED_USER_APPS = {
    "antigravity.exe", "code.exe", "chrome.exe", "msedge.exe", "firefox.exe",
    "brave.exe", "opera.exe", "opera_gx.exe", "notepad.exe", "notepad++.exe",
    "sublime_text.exe", "windowsterminal.exe", "cmd.exe", "powershell.exe",
    "pwsh.exe", "bash.exe", "git-bash.exe", "mintty.exe", "slack.exe",
    "discord.exe", "spotify.exe", "teams.exe", "ms-teams.exe", "postman.exe",
    "cursor.exe", "vlc.exe", "wordpad.exe", "winword.exe", "excel.exe",
    "powerpnt.exe", "outlook.exe", "acrobat.exe", "acrord32.exe", "steam.exe",
    "epicgameslauncher.exe", "telegram.exe", "whatsapp.exe", "zoom.exe",
    "rider64.exe", "idea64.exe", "pycharm64.exe", "clion64.exe", "goland64.exe",
    "webstorm64.exe", "githubdesktop.exe", "gitkraken.exe", "docker desktop.exe",
    "com.docker.backend.exe", "docker.exe", "obs64.exe", "obs32.exe", "obs.exe",
    "7zfm.exe", "7zg.exe", "winrar.exe",
}

APP_PROCESS_MAPPING: Dict[str, Dict[str, Any]] = {
    "AntiGravity": {"processes": {"antigravity.exe"}, "keywords": ["antigravity"]},
    "Visual Studio Code": {"processes": {"code.exe", "cursor.exe"}, "keywords": ["visual studio code", "cursor"]},
    "JetBrains IDEs": {
        "processes": {"idea64.exe", "pycharm64.exe", "rider64.exe", "clion64.exe", "goland64.exe", "webstorm64.exe"},
        "keywords": ["intellij", "pycharm", "rider", "jetbrains", "clion", "webstorm"],
    },
    "Sublime Text": {"processes": {"sublime_text.exe"}, "keywords": ["sublime"]},
    "Postman": {"processes": {"postman.exe"}, "keywords": ["postman"]},
    "GitHub Desktop": {"processes": {"githubdesktop.exe"}, "keywords": ["github desktop", "githubdesktop", "github"]},
    "GitKraken": {"processes": {"gitkraken.exe"}, "keywords": ["gitkraken"]},
    "Docker Desktop": {"processes": {"docker desktop.exe", "com.docker.backend.exe", "docker.exe"}, "keywords": ["docker desktop", "docker"]},
    "Google Chrome": {"processes": {"chrome.exe"}, "keywords": ["google chrome", "chrome"]},
    "Microsoft Edge": {"processes": {"msedge.exe"}, "keywords": ["microsoft edge", "msedge"]},
    "Mozilla Firefox": {"processes": {"firefox.exe"}, "keywords": ["mozilla firefox", "firefox"]},
    "Brave Browser": {"processes": {"brave.exe"}, "keywords": ["brave"]},
    "Opera Browser": {"processes": {"opera.exe", "opera_gx.exe"}, "keywords": ["opera"]},
    "Microsoft Word": {"processes": {"winword.exe"}, "keywords": ["word", "winword"]},
    "Microsoft Excel": {"processes": {"excel.exe"}, "keywords": ["excel"]},
    "Microsoft PowerPoint": {"processes": {"powerpnt.exe"}, "keywords": ["powerpoint", "powerpnt"]},
    "Microsoft Outlook": {"processes": {"outlook.exe"}, "keywords": ["outlook"]},
    "Notepad": {"processes": {"notepad.exe", "notepad++.exe", "wordpad.exe"}, "keywords": ["notepad", "wordpad"]},
    "Adobe Acrobat Reader": {"processes": {"acrobat.exe", "acrord32.exe"}, "keywords": ["acrobat", "adobe reader", "adobe acrobat"]},
    "Slack / Discord": {"processes": {"slack.exe", "discord.exe"}, "keywords": ["slack", "discord"]},
    "Telegram": {"processes": {"telegram.exe"}, "keywords": ["telegram"]},
    "WhatsApp": {"processes": {"whatsapp.exe"}, "keywords": ["whatsapp"]},
    "Zoom": {"processes": {"zoom.exe"}, "keywords": ["zoom"]},
    "Microsoft Teams": {"processes": {"teams.exe", "ms-teams.exe"}, "keywords": ["teams"]},
    "VLC Media Player": {"processes": {"vlc.exe"}, "keywords": ["vlc"]},
    "Spotify": {"processes": {"spotify.exe"}, "keywords": ["spotify"]},
    "Steam": {"processes": {"steam.exe"}, "keywords": ["steam"]},
    "Epic Games": {"processes": {"epicgameslauncher.exe"}, "keywords": ["epic games", "epicgameslauncher"]},
    "OBS Studio": {"processes": {"obs64.exe", "obs32.exe", "obs.exe"}, "keywords": ["obs", "obs studio"]},
    "Windows Terminal": {"processes": {"windowsterminal.exe"}, "keywords": ["windows terminal", "windowsterminal"]},
    "Command Prompt / PowerShell": {
        "processes": {"cmd.exe", "powershell.exe", "pwsh.exe", "bash.exe", "git-bash.exe", "mintty.exe"},
        "keywords": ["command prompt", "powershell", "cmd.exe", "windowspowershell"],
    },
    "7-Zip": {"processes": {"7zfm.exe", "7zg.exe"}, "keywords": ["7-zip", "7zfm", "7zg"]},
    "WinRAR": {"processes": {"winrar.exe"}, "keywords": ["winrar"]},
}

DEFAULT_APP_CLOSING_TARGETS: Dict[str, bool] = {name: True for name in APP_PROCESS_MAPPING}

__all__ = [
    "CRITICAL_OS_WHITELIST",
    "TARGETED_USER_APPS",
    "DEFAULT_APP_CLOSING_TARGETS",
    "APP_PROCESS_MAPPING",
]
