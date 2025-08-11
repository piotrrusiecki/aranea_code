#!/usr/bin/env python3
"""
Test script for voice configuration endpoints
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.robot_config import VOICE_AUTOSTART, VOICE_LANG

def test_voice_config():
    """Test voice configuration functionality"""
    print("Testing voice configuration...")
    
    # Test 1: Configuration values
    print("\n1. Testing configuration values...")
    print(f"   VOICE_AUTOSTART: {VOICE_AUTOSTART}")
    print(f"   VOICE_LANG: {VOICE_LANG}")
    assert isinstance(VOICE_AUTOSTART, bool), "VOICE_AUTOSTART should be boolean"
    assert isinstance(VOICE_LANG, str), "VOICE_LANG should be string"
    
    # Test 2: Configuration file structure
    print("\n2. Testing configuration file structure...")
    config_path = "config/robot_config.py"
    assert os.path.exists(config_path), f"Config file {config_path} should exist"
    
    with open(config_path, 'r') as f:
        content = f.read()
    
    assert "VOICE_AUTOSTART" in content, "VOICE_AUTOSTART should be in config file"
    assert "VOICE_LANG" in content, "VOICE_LANG should be in config file"
    
    print("   Config file structure is valid")
    
    # Test 3: Configuration file parsing
    print("\n3. Testing configuration file parsing...")
    lines = content.split('\n')
    voice_autostart_line = None
    voice_lang_line = None
    
    for line in lines:
        if line.strip().startswith('VOICE_AUTOSTART'):
            voice_autostart_line = line.strip()
        elif line.strip().startswith('VOICE_LANG'):
            voice_lang_line = line.strip()
    
    assert voice_autostart_line, "VOICE_AUTOSTART line should be found"
    assert voice_lang_line, "VOICE_LANG line should be found"
    
    print(f"   VOICE_AUTOSTART line: {voice_autostart_line}")
    print(f"   VOICE_LANG line: {voice_lang_line}")
    
    print("\n✅ All voice configuration tests passed!")

if __name__ == "__main__":
    test_voice_config()
