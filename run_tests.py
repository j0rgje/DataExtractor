#!/usr/bin/env python3
"""
Test runner voor HSO Data Extractor
Voert alle unit tests uit en genereert een test rapport
"""

import unittest
import sys
import os
import time
from io import StringIO

def run_all_tests():
    """Run alle tests en genereer rapport"""
    
    print("🧪 HSO Data Extractor - Test Suite")
    print("=" * 50)
    
    # Discover en load alle tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Create test runner met uitgebreide output
    stream = StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=2,
        buffer=True
    )
    
    # Run tests
    start_time = time.time()
    result = runner.run(test_suite)
    end_time = time.time()
    
    # Print resultaten
    print(f"\n📊 Test Resultaten:")
    print(f"   ✅ Tests geslaagd: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   ❌ Tests gefaald: {len(result.failures)}")
    print(f"   🚨 Errors: {len(result.errors)}")
    print(f"   ⏱️  Uitvoeringstijd: {end_time - start_time:.2f} seconden")
    
    # Print detailed output
    print(f"\n📝 Gedetailleerde Output:")
    print("-" * 30)
    print(stream.getvalue())
    
    # Print failures als ze er zijn
    if result.failures:
        print(f"\n❌ Gefaalde Tests:")
        print("-" * 20)
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    # Print errors als ze er zijn
    if result.errors:
        print(f"\n🚨 Test Errors:")
        print("-" * 15)
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    # Success rate
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n📈 Slagingspercentage: {success_rate:.1f}%")
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests
    exit_code = run_all_tests()
    
    print(f"\n{'✅ Alle tests geslaagd!' if exit_code == 0 else '❌ Sommige tests gefaald!'}")
    sys.exit(exit_code)
