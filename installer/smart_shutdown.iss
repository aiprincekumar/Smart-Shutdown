; Smart Shutdown - Inno Setup 6 Installer Script
; Developer: Atul Verma (aiprincekumar)

#define MyAppName "Smart Shutdown"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Atul Verma"
#define MyAppURL "https://github.com/aiprincekumar/smart-shutdown"
#define MyAppExeName "SmartShutdown.exe"

[Setup]
AppId={{8F4E2C1A-9B7D-4E3A-A1C5-6D2E8F0A3B4C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\output
OutputBaseFilename=Setup_Smart_Shutdown_v1.0.0
SetupIconFile=..\assets\smart_shutdown.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
WizardStyle=modern
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Start {#MyAppName} (Mini HUD) automatically with Windows"; GroupDescription: "Startup Options:"; Flags: unchecked

[Files]
Source: "..\dist\smart_shutdown.dist\*"; DestDir: "{app}"; Excludes: "_nuitka_temp.exe"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\Smart_Shutdown"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--mini-hud"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{sys}\taskkill.exe"; Parameters: "/F /IM {#MyAppExeName}"; Flags: runhidden; RunOnceId: "KillSmartShutdown"

[UninstallDelete]
Type: filesandordirs; Name: "{app}\*"
Type: files; Name: "{userstartup}\Smart_Shutdown.lnk"
