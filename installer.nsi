!include "MUI2.nsh"

Name "UWU Languaged"
OutFile "UWU_Languaged_Installer.exe"
InstallDir "$PROGRAMFILES\UWU Languaged"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "MainSection"
  SetOutPath "$INSTDIR"
  ; This copies your actual exe from your folder to the Program Files folder
  File "C:\Users\Garre\Downloads\uwulanguaged\dist\uwu_languaged.exe"
  File "app_icon.ico"
  
  ; Create Shortcuts
  CreateShortCut "$SMPROGRAMS\UWU Languaged.lnk" "$INSTDIR\uwu_languaged.exe" "" "$INSTDIR\app_icon.ico"
  CreateShortCut "$DESKTOP\UWU Languaged.lnk" "$INSTDIR\uwu_languaged.exe" "" "$INSTDIR\app_icon.ico"
SectionEnd