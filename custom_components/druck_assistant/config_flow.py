"""Config flow for the 3D-Druck-Assistant integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    BAMBU_DOMAIN,
    CONF_BAMBU_ENTRY_ID,
    CONF_NOTIFY_FILAMENT_LOW,
    CONF_PRICE_PER_KG,
    CONF_SERIAL,
    DEFAULT_FILAMENT_LOW,
    DEFAULT_PRICE_PER_KG,
    DOMAIN,
)


class DruckAssistantConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        printers = {
            e.entry_id: e
            for e in self.hass.config_entries.async_entries(BAMBU_DOMAIN)
            if e.data.get(CONF_SERIAL)
        }
        if not printers:
            return self.async_abort(reason="no_bambu_lab")

        if user_input is not None:
            bambu = printers[user_input[CONF_BAMBU_ENTRY_ID]]
            await self.async_set_unique_id(bambu.data[CONF_SERIAL])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=bambu.title,
                data={
                    CONF_BAMBU_ENTRY_ID: bambu.entry_id,
                    CONF_SERIAL: bambu.data[CONF_SERIAL],
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_BAMBU_ENTRY_ID): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value=eid, label=e.title)
                            for eid, e in printers.items()
                        ]
                    )
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return DruckAssistantOptionsFlow()


class DruckAssistantOptionsFlow(OptionsFlow):
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        opts = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_PRICE_PER_KG,
                    default=opts.get(CONF_PRICE_PER_KG, DEFAULT_PRICE_PER_KG),
                ): vol.All(vol.Coerce(float), vol.Range(min=0)),
                vol.Required(
                    CONF_NOTIFY_FILAMENT_LOW,
                    default=opts.get(CONF_NOTIFY_FILAMENT_LOW, DEFAULT_FILAMENT_LOW),
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
