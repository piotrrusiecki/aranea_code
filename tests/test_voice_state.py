#!/usr/bin/env python3
"""
Test script for voice control state management
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from robot_state import RobotState
from voice_manager import VoiceManager
from config import robot_config

logger = logging.getLogger("test.voice_state")

def test_voice_state_management():
    """Test voice control state management."""
    logger.info("Testing voice control state management")
    
    try:
        # Test 1: Robot state initialization
        logger.info("1. Testing robot state initialization")
        robot_state = RobotState()
        voice_active = robot_state.get_flag("voice_active")
        logger.debug("   Initial voice_active state: %s", voice_active)
        
        # Should start as False
        assert voice_active == False, "voice_active should start as False"
        
        # Test 2: Direct robot state manipulation
        logger.info("2. Testing direct robot state manipulation")
        robot_state.set_flag("voice_active", True)
        voice_active = robot_state.get_flag("voice_active")
        logger.debug("   Voice active after setting to True: %s", voice_active)
        assert voice_active == True, "voice_active should be True after setting"
        
        robot_state.set_flag("voice_active", False)
        voice_active = robot_state.get_flag("voice_active")
        logger.debug("   Voice active after setting to False: %s", voice_active)
        assert voice_active == False, "voice_active should be False after setting"
        
        # Test 3: Voice manager state tracking
        logger.info("3. Testing voice manager state tracking")
        voice_manager = VoiceManager()
        
        logger.debug("   Voice manager initial state:")
        logger.debug("     voice_active: %s", voice_manager.voice_active)
        logger.debug("     voice: %s", voice_manager.voice)
        logger.debug("     voice_thread: %s", voice_manager.voice_thread)
        
        # Should start as inactive
        assert voice_manager.voice_active == False, "Voice manager should start inactive"
        assert voice_manager.voice is None, "Voice control should start as None"
        assert voice_manager.voice_thread is None, "Voice thread should start as None"
        
        # Test 4: Configuration
        logger.info("4. Testing configuration")
        VOICE_AUTOSTART = robot_config.VOICE_AUTOSTART
        VOICE_LANG = robot_config.VOICE_LANG
        logger.debug("   VOICE_AUTOSTART: %s", VOICE_AUTOSTART)
        logger.debug("   VOICE_LANG: %s", VOICE_LANG)
        
        # Test 5: Robot state flag management
        logger.info("5. Testing robot state flag management")
        all_flags = robot_state.get_all_flags()
        logger.debug("   All flags: %s", all_flags)
        
        # Check that voice_active flag exists
        assert "voice_active" in all_flags, "voice_active flag should exist in robot state"
        
        logger.info("✅ All voice state management tests passed")
        return True
        
    except Exception as e:
        logger.error("❌ Voice state management test failed: %s", e)
        return False

if __name__ == "__main__":
    # Configure logging for test
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s'
    )
    
    success = test_voice_state_management()
    if not success:
        exit(1)
