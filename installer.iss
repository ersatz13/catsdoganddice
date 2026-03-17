[Setup]
AppName=Cats Dogs and Dice
AppVersion=0.19
AppPublisher=Team Jibby
DefaultDirName={autopf}\Cats Dogs and Dice
DefaultGroupName=Cats Dogs and Dice
OutputBaseFilename=CatsDogsAndDiceInstaller_v019
OutputDir=dist_installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=Assets\UI\icon.ico
UninstallDisplayIcon={app}\Cats Dogs and Dice.exe

[Files]
Source: "dist\Cats Dogs and Dice.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "Assets\*"; DestDir: "{app}\Assets"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Cats Dogs and Dice"; Filename: "{app}\Cats Dogs and Dice.exe"; IconFilename: "{app}\Assets\UI\icon.ico"
Name: "{commondesktop}\Cats Dogs and Dice"; Filename: "{app}\Cats Dogs and Dice.exe"; Tasks: desktopicon; IconFilename: "{app}\Assets\UI\icon.ico"

[Tasks]
Name: "desktopicon"; Description: "Create a Desktop icon"; GroupDescription: "Additional icons:"
