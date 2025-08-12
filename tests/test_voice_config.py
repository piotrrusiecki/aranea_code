#!/usr/bin/env python3
"""
Test script for voice configuration endpoints
"""

import os
import logging
from config import robot_config

logger = logging.getLogger("test.voice_config")

def test_voice_configuration():
    """Test voice configuration settings."""
    logger.info("Testing voice configuration")
    
    try:
        # Test 1: Configuration values
        logger.info("1. Testing configuration values")
        VOICE_AUTOSTART = robot_config.VOICE_AUTOSTART
        VOICE_LANG = robot_config.VOICE_LANG
        
        logger.debug("   VOICE_AUTOSTART: %s", VOICE_AUTOSTART)
        logger.debug("   VOICE_LANG: %s", VOICE_LANG)
        
        # Validate configuration values
        assert isinstance(VOICE_AUTOSTART, bool), "VOICE_AUTOSTART must be boolean"
        assert isinstance(VOICE_LANG, str), "VOICE_LANG must be string"
        assert VOICE_LANG in robot_config.VOICE_MODELS, f"VOICE_LANG '{VOICE_LANG}' not in supported models"
        
        # Test 2: Configuration file structure
        logger.info("2. Testing configuration file structure")
        config_file_path = "config/robot_config.py"
        
        if not os.path.exists(config_file_path):
            logger.error("Configuration file not found: %s", config_file_path)
            return False
        
        with open(config_file_path, 'r') as f:
            config_content = f.read()
        
        # Check for required configuration variables
        required_vars = ['VOICE_AUTOSTART', 'VOICE_LANG', 'VOICE_MODELS']
        for var in required_vars:
            if var not in config_content:
                logger.error("Missing required configuration variable: %s", var)
                return False
        
        logger.info("   Config file structure is valid")
        
        # Test 3: Configuration file parsing
        logger.info("3. Testing configuration file parsing")
        
        # Check if voice models are properly defined
        voice_models = robot_config.VOICE_MODELS
        assert isinstance(voice_models, dict), "VOICE_MODELS must be dictionary"
        
        # Check for specific language entries
        expected_languages = ['en', 'de', 'fr', 'es', 'pl', 'pt', 'hi', 'eo']
        for lang in expected_languages:
            if lang not in voice_models:
                logger.warning("Missing voice model for language: %s", lang)
        
        # Check configuration file content for specific lines
        voice_autostart_line = f"VOICE_AUTOSTART = {VOICE_AUTOSTART}"
        voice_lang_line = f"VOICE_LANG = \"{VOICE_LANG}\""
        
        if voice_autostart_line not in config_content:
            logger.warning("VOICE_AUTOSTART line not found in expected format")
        
        if voice_lang_line not in config_content:
            logger.warning("VOICE_LANG line not found in expected format")
        
        logger.debug("   VOICE_AUTOSTART line: %s", voice_autostart_line)
        logger.debug("   VOICE_LANG line: %s", voice_lang_line)
        
        logger.info("✅ All voice configuration tests passed")
        return True
        
    except Exception as e:
        logger.error("❌ Voice configuration test failed: %s", e)
        return False

if __name__ == "__main__":
    # Configure logging for test
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s'
    )
    
    success = test_voice_configuration()
    if not success:
        exit(1)
