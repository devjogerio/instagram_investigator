#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal para executar todos os testes do Instagram Investigator

Este script executa todos os testes automatizados do projeto, incluindo:
- Testes do sistema de cache
- Testes das APIs das plataformas
- Testes do analisador cross-platform
- Testes das visualizações

Uso:
    python test_runner.py [--verbose] [--coverage] [--module MODULE_NAME]
"""

import unittest
import sys
import os
import argparse
from io import StringIO

# Adiciona o diretório raiz do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests(verbose=False, coverage=False, module=None):
    """
    Executa os testes do projeto
    
    Args:
        verbose (bool): Se True, exibe saída detalhada
        coverage (bool): Se True, executa com análise de cobertura
        module (str): Nome do módulo específico para testar
    
    Returns:
        bool: True se todos os testes passaram, False caso contrário
    """
    # Configura o loader de testes
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Define os módulos de teste
    test_modules = [
        'test_cache_manager',
        'test_apis',
        'test_cross_platform'
    ]
    
    # Se um módulo específico foi especificado, testa apenas ele
    if module:
        if module in test_modules:
            test_modules = [module]
        else:
            print(f"Erro: Módulo '{module}' não encontrado.")
            print(f"Módulos disponíveis: {', '.join(test_modules)}")
            return False
    
    # Carrega os testes
    tests_loaded = 0
    for test_module in test_modules:
        try:
            module_suite = loader.loadTestsFromName(test_module)
            suite.addTest(module_suite)
            tests_loaded += module_suite.countTestCases()
            if verbose:
                print(f"✓ Carregado módulo: {test_module}")
        except Exception as e:
            print(f"✗ Erro ao carregar {test_module}: {e}")
            return False
    
    print(f"\n📋 Total de testes carregados: {tests_loaded}")
    print("=" * 60)
    
    # Configura o runner
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        stream=sys.stdout,
        buffer=True
    )
    
    # Executa os testes
    if coverage:
        try:
            import coverage as cov
            
            # Inicia a análise de cobertura
            cov_instance = cov.Coverage()
            cov_instance.start()
            
            print("🔍 Executando testes com análise de cobertura...\n")
            result = runner.run(suite)
            
            # Para a análise de cobertura
            cov_instance.stop()
            cov_instance.save()
            
            # Gera relatório de cobertura
            print("\n" + "=" * 60)
            print("📊 RELATÓRIO DE COBERTURA")
            print("=" * 60)
            cov_instance.report()
            
        except ImportError:
            print("⚠️  Módulo 'coverage' não encontrado. Executando sem análise de cobertura.")
            result = runner.run(suite)
    else:
        print("🧪 Executando testes...\n")
        result = runner.run(suite)
    
    # Exibe resumo dos resultados
    print("\n" + "=" * 60)
    print("📈 RESUMO DOS RESULTADOS")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    success = total_tests - failures - errors - skipped
    
    print(f"✅ Sucessos: {success}/{total_tests}")
    if failures > 0:
        print(f"❌ Falhas: {failures}")
    if errors > 0:
        print(f"💥 Erros: {errors}")
    if skipped > 0:
        print(f"⏭️  Ignorados: {skipped}")
    
    success_rate = (success / total_tests * 100) if total_tests > 0 else 0
    print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
    
    # Exibe detalhes dos erros e falhas
    if failures > 0 or errors > 0:
        print("\n" + "=" * 60)
        print("🔍 DETALHES DOS PROBLEMAS")
        print("=" * 60)
        
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"\n❌ FALHA {i}: {test}")
            print("-" * 40)
            print(traceback)
        
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"\n💥 ERRO {i}: {test}")
            print("-" * 40)
            print(traceback)
    
    return result.wasSuccessful()

def check_dependencies():
    """
    Verifica se todas as dependências necessárias estão instaladas
    
    Returns:
        bool: True se todas as dependências estão disponíveis
    """
    required_modules = [
        'unittest',
        'requests',
        'matplotlib',
        'pandas',
        'networkx'
    ]
    
    optional_modules = [
        'coverage'
    ]
    
    missing_required = []
    missing_optional = []
    
    # Verifica módulos obrigatórios
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_required.append(module)
    
    # Verifica módulos opcionais
    for module in optional_modules:
        try:
            __import__(module)
        except ImportError:
            missing_optional.append(module)
    
    if missing_required:
        print("❌ Dependências obrigatórias não encontradas:")
        for module in missing_required:
            print(f"   - {module}")
        print("\nInstale as dependências com: pip install -r requirements.txt")
        return False
    
    if missing_optional:
        print("⚠️  Dependências opcionais não encontradas:")
        for module in missing_optional:
            print(f"   - {module}")
        print("\nPara análise de cobertura, instale: pip install coverage")
    
    return True

def main():
    """
    Função principal do script
    """
    parser = argparse.ArgumentParser(
        description='Executa os testes automatizados do Instagram Investigator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python test_runner.py                    # Executa todos os testes
  python test_runner.py --verbose          # Executa com saída detalhada
  python test_runner.py --coverage         # Executa com análise de cobertura
  python test_runner.py --module test_apis # Executa apenas testes das APIs
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Exibe saída detalhada dos testes'
    )
    
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Executa análise de cobertura de código'
    )
    
    parser.add_argument(
        '--module', '-m',
        type=str,
        help='Executa apenas os testes do módulo especificado'
    )
    
    args = parser.parse_args()
    
    print("🧪 INSTAGRAM INVESTIGATOR - SUITE DE TESTES")
    print("=" * 60)
    
    # Verifica dependências
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ Todas as dependências obrigatórias estão disponíveis\n")
    
    # Executa os testes
    success = run_tests(
        verbose=args.verbose,
        coverage=args.coverage,
        module=args.module
    )
    
    # Define o código de saída
    exit_code = 0 if success else 1
    
    if success:
        print("\n🎉 Todos os testes passaram com sucesso!")
    else:
        print("\n💥 Alguns testes falharam. Verifique os detalhes acima.")
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()