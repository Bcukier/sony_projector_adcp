"""Config flow for Sony Projector ADCP integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_USE_AUTH,
    DEFAULT_NAME,
    DEFAULT_PASSWORD,
    DEFAULT_PORT,
    DEFAULT_USE_AUTH,
    DOMAIN,
)
from .protocol import SonyProjectorADCP

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the user input allows us to connect."""
    projector = SonyProjectorADCP(
        host=data[CONF_HOST],
        port=data[CONF_PORT],
        password=data.get(CONF_PASSWORD, ""),
        use_auth=data.get(CONF_USE_AUTH, True),
    )

    # Test connection
    if not await projector.connect():
        raise ConnectionError("Cannot connect to projector")

    await projector.disconnect()

    return {"title": data.get(CONF_NAME, DEFAULT_NAME)}


class SonyProjectorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sony Projector ADCP."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Check if already configured
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()

            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Optional(CONF_USE_AUTH, default=DEFAULT_USE_AUTH): bool,
                vol.Optional(CONF_PASSWORD, default=DEFAULT_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return SonyProjectorOptionsFlow(config_entry)


class SonyProjectorOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Sony Projector ADCP."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_USE_AUTH,
                        default=self.config_entry.data.get(
                            CONF_USE_AUTH, DEFAULT_USE_AUTH
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_PASSWORD,
                        default=self.config_entry.data.get(
                            CONF_PASSWORD, DEFAULT_PASSWORD
                        ),
                    ): str,
                }
            ),
        )
