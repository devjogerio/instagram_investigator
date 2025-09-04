#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Build para Instagram Investigator
Gera executável standalone usando PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build_directories():
    """Remove diretórios de build anteriores"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Removendo diretório: {dir_name}")
            shutil.rmtree(dir_name)
    
    # Remove arquivos .spec anteriores
    for spec_file in Path('.').glob('*.spec'):
        print(f"Removendo arquivo spec: {spec_file}")
        spec_file.unlink()

def create_pyinstaller_spec():
    """Cria arquivo .spec personalizado para PyInstaller"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['tkinter_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('modules', 'modules'),
        ('config', 'config'),
        ('docs', 'docs'),
        ('.env.example', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'matplotlib.backends.backend_tkagg',
        'PIL._tkinter_finder',
        'requests',
        'nltk',
        'sklearn',
        'numpy',
        'pandas',
        'networkx',
        'seaborn',
        'reportlab',
        'openpyxl',
        'xlsxwriter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='InstagramInvestigator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
'''
    
    with open('instagram_investigator.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("Arquivo .spec criado: instagram_investigator.spec")

def build_executable():
    """Executa o build do executável"""
    print("Iniciando build do executável...")
    
    try:
        # Executa PyInstaller com o arquivo .spec
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            'instagram_investigator.spec'
        ], check=True, capture_output=True, text=True)
        
        print("Build concluído com sucesso!")
        print(f"Executável criado em: {os.path.abspath('dist')}")
        
    except subprocess.CalledProcessError as e:
        print(f"Erro durante o build: {e}")
        print(f"Saída do erro: {e.stderr}")
        return False
    
    return True

def create_installer_structure():
    """Cria estrutura para instalador"""
    installer_dir = Path('installer')
    installer_dir.mkdir(exist_ok=True)
    
    # Copia executável
    if os.path.exists('dist/InstagramInvestigator.exe'):
        shutil.copy2('dist/InstagramInvestigator.exe', installer_dir)
    
    # Cria arquivo de instalação
    install_script = '''
@echo off
echo Instalando Instagram Investigator...

set INSTALL_DIR=%PROGRAMFILES%\\InstagramInvestigator

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

copy "InstagramInvestigator.exe" "%INSTALL_DIR%\\"
copy ".env.example" "%INSTALL_DIR%\\"

echo Criando atalho na área de trabalho...
set DESKTOP=%USERPROFILE%\\Desktop
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\\Instagram Investigator.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\\InstagramInvestigator.exe" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs
del CreateShortcut.vbs

echo Instalação concluída!
echo O Instagram Investigator foi instalado em: %INSTALL_DIR%
echo Um atalho foi criado na área de trabalho.
pause
'''
    
    with open(installer_dir / 'install.bat', 'w', encoding='utf-8') as f:
        f.write(install_script)
    
    # Copia arquivo .env.example
    if os.path.exists('.env.example'):
        shutil.copy2('.env.example', installer_dir)
    
    print(f"Estrutura do instalador criada em: {installer_dir.absolute()}")

def main():
    """Função principal do script de build"""
    print("=== Instagram Investigator - Script de Build ===")
    print("Preparando build do executável...\n")
    
    # Verifica se PyInstaller está instalado
    try:
        import PyInstaller
        print(f"PyInstaller encontrado: versão {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller não encontrado. Instalando...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
    
    # Limpa diretórios anteriores
    clean_build_directories()
    
    # Cria arquivo .spec
    create_pyinstaller_spec()
    
    # Executa build
    if build_executable():
        print("\n=== Build Concluído ===")
        
        # Cria estrutura do instalador
        create_installer_structure()
        
        print("\nArquivos gerados:")
        print(f"- Executável: {os.path.abspath('dist/InstagramInvestigator.exe')}")
        print(f"- Instalador: {os.path.abspath('installer')}")
        
        print("\nPara distribuir:")
        print("1. Teste o executável em dist/InstagramInvestigator.exe")
        print("2. Use os arquivos em installer/ para distribuição")
        print("3. Execute install.bat como administrador no computador de destino")
    else:
        print("\nBuild falhou. Verifique os erros acima.")
        sys.exit(1)

if __name__ == '__main__':
    main()