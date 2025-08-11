#!/usr/bin/env python3
"""
Test script for voice control state management
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from robot_state import RobotState
from voice_manager import VoiceManager
from config.robot_config import VOICE_AUTOSTART, VOICE_LANG

def test_voice_state_management():
    """Test voice control state management functionality"""
    print("Testing voice control state management...")
    
    # Test 1: Robot state initialization
    print("\n1. Testing robot state initialization...")
    robot_state = RobotState()
    voice_active = robot_state.get_flag("voice_active")
    print(f"   Initial voice_active state: {voice_active}")
    assert voice_active is False, "Voice should be inactive by default"
    
    # Test 2: Direct robot state manipulation
    print("\n2. Testing direct robot state manipulation...")
    robot_state.set_flag("voice_active", True)
    voice_active = robot_state.get_flag("voice_active")
    print(f"   Voice active after setting to True: {voice_active}")
    assert voice_active is True, "Voice should be active after setting to True"
    
    robot_state.set_flag("voice_active", False)
    voice_active = robot_state.get_flag("voice_active")
    print(f"   Voice active after setting to False: {voice_active}")
    assert voice_active is False, "Voice should be inactive after setting to False"
    
    # Test 3: Voice manager state tracking (without actual voice control)
    print("\n3. Testing voice manager state tracking...")
    voice_manager = VoiceManager()
    
    # Mock command sender and ultrasonic sensor
    def mock_command_sender(cmd):
        print(f"   Mock command sent: {cmd}")
    
    class MockUltrasonicSensor:
        def __init__(self):
            self.distance = 100
    
    ultrasonic_sensor = MockUltrasonicSensor()
    
    # Test voice manager internal state
    print("   Voice manager initial state:")
    print(f"     voice_active: {voice_manager.voice_active}")
    print(f"     voice: {voice_manager.voice}")
    print(f"     voice_thread: {voice_manager.voice_thread}")
    
    # Test 4: Configuration
    print("\n4. Testing configuration...")
    print(f"   VOICE_AUTOSTART: {VOICE_AUTOSTART}")
    print(f"   VOICE_LANG: {VOICE_LANG}")
    assert isinstance(VOICE_AUTOSTART, bool), "VOICE_AUTOSTART should be boolean"
    assert isinstance(VOICE_LANG, str), "VOICE_LANG should be string"
    
    # Test 5: Robot state flag management
    print("\n5. Testing robot state flag management...")
    all_flags = robot_state.get_all_flags()
    print(f"   All flags: {all_flags}")
    assert "voice_active" in all_flags, "voice_active flag should be in robot state"
    
    print("\n✅ All voice state management tests passed!")

if __name__ == "__main__":
    test_voice_state_management()
