"""Sony ADCP Protocol Handler."""
import asyncio
import hashlib
import logging
from typing import Optional

_LOGGER = logging.getLogger(__name__)

NEWLINE = "\r\n"
ENCODING = "ascii"
TIMEOUT = 10


class SonyProjectorADCP:
    """Handle ADCP protocol communication with Sony projector."""

    def __init__(self, host: str, port: int, password: str = "", use_auth: bool = True):
        """Initialize the ADCP connection."""
        self.host = host
        self.port = port
        self.password = password
        self.use_auth = use_auth
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._lock = asyncio.Lock()

    async def connect(self) -> bool:
        """Connect to the projector and authenticate if needed."""
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=TIMEOUT
            )
            
            # Read authentication challenge
            auth_response = await self._read_line()
            
            if auth_response.startswith("PJLINK") or not self.use_auth:
                # If we get PJLINK or auth is disabled, we might need different handling
                # For now, just continue
                if auth_response == "NOKEY":
                    _LOGGER.debug("Authentication disabled on projector")
                    return True
            
            # Authentication enabled - handle random number
            if self.use_auth and auth_response:
                # Response format: random_number\r\n
                random_num = auth_response.strip()
                
                if random_num and random_num != "NOKEY":
                    # Create hash: SHA256(random_number + password)
                    hash_input = f"{random_num}{self.password}"
                    hash_result = hashlib.sha256(hash_input.encode()).hexdigest()
                    
                    # Send hash
                    await self._write_line(hash_result)
                    
                    # Read authentication result
                    auth_result = await self._read_line()
                    
                    if auth_result != "OK":
                        _LOGGER.error("Authentication failed: %s", auth_result)
                        await self.disconnect()
                        return False
            
            _LOGGER.info("Connected to Sony projector at %s:%s", self.host, self.port)
            return True
            
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout connecting to projector")
            return False
        except Exception as e:
            _LOGGER.error("Error connecting to projector: %s", e)
            return False

    async def disconnect(self):
        """Disconnect from the projector."""
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception as e:
                _LOGGER.debug("Error closing connection: %s", e)
            finally:
                self._writer = None
                self._reader = None

    async def _read_line(self) -> str:
        """Read a line from the projector."""
        if not self._reader:
            raise ConnectionError("Not connected")
        
        try:
            data = await asyncio.wait_for(
                self._reader.readuntil(NEWLINE.encode(ENCODING)),
                timeout=TIMEOUT
            )
            return data.decode(ENCODING).strip()
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout reading from projector")
            raise
        except Exception as e:
            _LOGGER.error("Error reading from projector: %s", e)
            raise

    async def _write_line(self, data: str):
        """Write a line to the projector."""
        if not self._writer:
            raise ConnectionError("Not connected")
        
        try:
            self._writer.write(f"{data}{NEWLINE}".encode(ENCODING))
            await self._writer.drain()
        except Exception as e:
            _LOGGER.error("Error writing to projector: %s", e)
            raise

    async def send_command(self, command: str) -> Optional[str]:
        """Send a command and return the response."""
        async with self._lock:
            # Ensure we're connected
            if not self._writer or not self._reader:
                if not await self.connect():
                    return None
            
            try:
                # Send command
                await self._write_line(command)
                _LOGGER.debug("Sent command: %s", command)
                
                # Read response
                response = await self._read_line()
                _LOGGER.debug("Received response: %s", response)
                
                # Check for errors
                if response.startswith("err_"):
                    _LOGGER.error("Command error: %s for command: %s", response, command)
                    return None
                
                return response
                
            except Exception as e:
                _LOGGER.error("Error sending command %s: %s", command, e)
                await self.disconnect()
                return None

    async def get_power_status(self) -> Optional[str]:
        """Get the current power status."""
        response = await self.send_command("power_status ?")
        if response and response.startswith('"') and response.endswith('"'):
            return response.strip('"')
        return None

    async def set_power(self, state: bool) -> bool:
        """Set power on or off."""
        command = 'power "on"' if state else 'power "off"'
        response = await self.send_command(command)
        return response == "ok"

    async def get_input(self) -> Optional[str]:
        """Get current input source."""
        response = await self.send_command("input ?")
        if response and response.startswith('"') and response.endswith('"'):
            return response.strip('"')
        return None

    async def set_input(self, source: str) -> bool:
        """Set input source."""
        command = f'input "{source}"'
        response = await self.send_command(command)
        return response == "ok"

    async def get_blank_status(self) -> Optional[bool]:
        """Get video muting status."""
        response = await self.send_command("blank ?")
        if response and response.startswith('"') and response.endswith('"'):
            return response.strip('"') == "on"
        return None

    async def set_blank(self, state: bool) -> bool:
        """Set video muting."""
        command = 'blank "on"' if state else 'blank "off"'
        response = await self.send_command(command)
        return response == "ok"

    async def get_picture_mode(self) -> Optional[str]:
        """Get current picture mode."""
        response = await self.send_command("picture_mode ?")
        if response and response.startswith('"') and response.endswith('"'):
            return response.strip('"')
        return None

    async def set_picture_mode(self, mode: str) -> bool:
        """Set picture mode."""
        command = f'picture_mode "{mode}"'
        response = await self.send_command(command)
        return response == "ok"

    async def get_numeric_value(self, parameter: str) -> Optional[int]:
        """Get a numeric parameter value."""
        response = await self.send_command(f"{parameter} ?")
        if response and response.isdigit():
            return int(response)
        # Handle negative numbers
        if response and response.lstrip('-').isdigit():
            return int(response)
        return None

    async def set_numeric_value(self, parameter: str, value: int) -> bool:
        """Set a numeric parameter value."""
        command = f"{parameter} {value}"
        response = await self.send_command(command)
        return response == "ok"

    async def send_key(self, key: str) -> bool:
        """Send a remote control key command."""
        command = f'key "{key}"'
        response = await self.send_command(command)
        return response == "ok"

    async def get_reality_creation(self) -> Optional[str]:
        """Get Reality Creation status."""
        response = await self.send_command("real_cre ?")
        if response and response.startswith('"') and response.endswith('"'):
            return response.strip('"')
        return None

    async def set_reality_creation(self, state: str) -> bool:
        """Set Reality Creation on/off."""
        command = f'real_cre "{state}"'
        response = await self.send_command(command)
        return response == "ok"