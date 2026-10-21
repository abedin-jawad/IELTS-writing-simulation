; =====================================================================
; INNO SETUP SCRIPT FOR: IELTS Writing Simulation Engine v1.0.0
; Publisher: Jawad Abedin
; =====================================================================

[Setup]
; Unique Application ID (Generated for version tracking & clean uninstall)
AppId={{D37B19A2-8F9E-4B52-9A08-2C768A45B101}

; Application Information
AppName=IELTS Writing Simulation Engine
AppVersion=1.0.0
AppPublisher=Jawad Abedin

; Default Installation Path: C:\Program Files\IELTS Writing Simulation Engine
DefaultDirName={autopf}\IELTS Writing Simulation Engine
DefaultGroupName=IELTS Writing Simulation Engine

; License / Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Output File Settings
OutputDir=D:\Output
OutputBaseFilename=IELTS_Writing_Simulation_Engine_Setup_v1.0.0
SetupIconFile=G:\Downloads\app_icon.ico

; Compression Settings (Maximum efficiency)
Compression=lzma2/ultra64
SolidCompression=yes

; Visual Style
WizardStyle=Windows11

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
; Main Executable
Source: "D:\dist\ielts_targeted_studio.exe"; DestDir: "{app}"; DestName: "IELTS_Writing_Simulation_Engine.exe"; Flags: ignoreversion

; App Custom Icon Asset
Source: "G:\Downloads\app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu Shortcuts
Name: "{group}\IELTS Writing Simulation Engine"; Filename: "{app}\IELTS_Writing_Simulation_Engine.exe"; IconFilename: "{app}\app_icon.ico"
Name: "{group}\{cm:UninstallProgram,IELTS Writing Simulation Engine}"; Filename: "{uninstallexe}"

; Desktop Shortcut
Name: "{autodesktop}\IELTS Writing Simulation Engine"; Filename: "{app}\IELTS_Writing_Simulation_Engine.exe"; IconFilename: "{app}\app_icon.ico"; Tasks: desktopicon

[Run]
; Option to launch app immediately after installation finishes
Filename: "{app}\IELTS_Writing_Simulation_Engine.exe"; Description: "{cm:LaunchProgram,IELTS Writing Simulation Engine}"; Flags: nowait postinstall skipifsilent