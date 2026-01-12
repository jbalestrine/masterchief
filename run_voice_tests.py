#!/usr/bin/env python3
"""Run all voice automation tests."""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """Run all voice automation tests."""
    test_dir = os.path.join(os.path.dirname(__file__), 'tests/test_voice/test_automation')
    test_files = [
        'test_wake_word.py',
        'test_intent_parser.py',
        'test_conversation.py',
    ]
    
    print("=" * 60)
    print("Running Voice Automation Tests")
    print("=" * 60)
    
    failed = []
    passed = []
    
    for test_file in test_files:
        test_path = os.path.join(test_dir, test_file)
        if not os.path.exists(test_path):
            print(f"\n⚠️  Test file not found: {test_file}")
            continue
        
        print(f"\n📋 Running {test_file}...")
        print("-" * 60)
        
        result = os.system(f'python {test_path}')
        
        if result == 0:
            passed.append(test_file)
        else:
            failed.append(test_file)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"✅ Passed: {len(passed)}")
    print(f"❌ Failed: {len(failed)}")
    
    if failed:
        print("\nFailed tests:")
        for test in failed:
            print(f"  - {test}")
        return 1
    else:
        print("\n🎉 All tests passed!")
        return 0

if __name__ == '__main__':
    sys.exit(run_tests())
