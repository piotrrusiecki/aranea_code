import os
import logging

logger = logging.getLogger("config.parameter")

class ParameterManager:
    def __init__(self):
        self.PARAM_FILE = "params.json"
        self.pcb_version = None
        self.pi_version = None
        self.load_parameters()

    def _validate_file_path(self, file_path):
        """Validate file path to prevent path traversal attacks."""
        try:
            if not file_path or not isinstance(file_path, str):
                raise ValueError("File path must be a non-empty string")
            
            # Remove any path separators and normalize
            basename = os.path.basename(file_path)
            if basename != file_path:
                raise ValueError("File path cannot contain path separators")
            
            # Check for dangerous characters
            dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
            for char in dangerous_chars:
                if char in file_path:
                    raise ValueError(f"File path contains invalid character: {char}")
            
            logger.debug("File path validation passed: %s", file_path)
            return basename
        except Exception as e:
            logger.error("File path validation failed for '%s': %s", file_path, e)
            raise

    def delete_file(self, file_path):
        """Delete a file with path validation."""
        try:
            validated_path = self._validate_file_path(file_path)
            if os.path.exists(validated_path):
                os.remove(validated_path)
                logger.info("Deleted %s", validated_path)
            else:
                logger.warning("File %s does not exist", validated_path)
        except Exception as e:
            logger.error("Invalid file path: %s", e)

    def file_exists(self, file_path):
        """Check if a file exists with path validation."""
        try:
            validated_path = self._validate_file_path(file_path)
            return os.path.exists(validated_path)
        except Exception as e:
            logger.error("Invalid file path: %s", e)
            return False

    @staticmethod
    def get_raspberry_pi_version():
        """Get Raspberry Pi version information."""
        try:
            # Read the model information from /proc/device-tree/model
            with open('/proc/device-tree/model', 'r') as f:
                model_info = f.read().strip()
            
            # Check if it's a Raspberry Pi 5
            if 'Raspberry Pi 5' in model_info:
                logger.debug("Detected Raspberry Pi 5")
                return 2
            else:
                logger.debug("Detected Raspberry Pi 4 or earlier")
                return 1
        except FileNotFoundError:
            logger.warning("Failed to get Raspberry Pi model information")
            return 1
        except Exception as e:
            logger.error("Error getting Raspberry Pi version: %s", e)
            return 1

    def load_parameters(self):
        """Load parameters from the JSON file."""
        try:
            if not os.path.exists(self.PARAM_FILE):
                logger.warning("Parameter file %s does not exist or contains invalid parameters", self.PARAM_FILE)
                self.create_parameter_file()
                return

            # Load parameters from file
            import json
            with open(self.PARAM_FILE, 'r') as f:
                data = json.load(f)
                self.pcb_version = data.get('pcb_version', 1)
                self.pi_version = data.get('pi_version', 1)
                
            logger.info("Parameters loaded - PCB v%d, Pi v%d", self.pcb_version, self.pi_version)
        except Exception as e:
            logger.error("Failed to load parameters: %s", e)
            self.create_parameter_file()

    def create_parameter_file(self):
        """Create a new parameter file with user input."""
        logger.info("Please enter the hardware versions")
        
        while True:
            try:
                pcb_input = input("Enter PCB Version (1 or 2): ").strip()
                pcb_version = int(pcb_input)
                
                if pcb_version not in [1, 2]:
                    logger.error("Invalid PCB Version. Please enter 1 or 2")
                    continue
                    
                break
            except ValueError:
                logger.error("Invalid input. Please enter a number")
                continue

        # Get Raspberry Pi version automatically
        pi_version = self.get_raspberry_pi_version()
        
        # Save to file
        import json
        data = {
            'pcb_version': pcb_version,
            'pi_version': pi_version
        }
        
        with open(self.PARAM_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.pcb_version = pcb_version
        self.pi_version = pi_version
        
        logger.info("PCB Version: %d.0", pcb_version)
        logger.info("Raspberry PI version is %s", 'less than 5' if pi_version == 1 else '5')

    def get_pcb_version(self):
        """Get the PCB version."""
        return self.pcb_version

    def get_pi_version(self):
        """Get the Raspberry Pi version."""
        return self.pi_version

    def update_parameters(self, pcb_version=None, pi_version=None):
        """Update parameters and save to file."""
        if pcb_version is not None:
            if pcb_version not in [1, 2]:
                logger.error("Invalid PCB version: %d", pcb_version)
                return False
            self.pcb_version = pcb_version
            
        if pi_version is not None:
            if pi_version not in [1, 2]:
                logger.error("Invalid Pi version: %d", pi_version)
                return False
            self.pi_version = pi_version
        
        # Save to file
        import json
        data = {
            'pcb_version': self.pcb_version,
            'pi_version': self.pi_version
        }
        
        with open(self.PARAM_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info("Parameters updated - PCB v%d, Pi v%d", self.pcb_version, self.pi_version)
        return True