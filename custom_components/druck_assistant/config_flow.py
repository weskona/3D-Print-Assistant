"""Config flow for the 3D Print Assistant integration."""

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
    CONF_AUTO_IMPORT,
    CONF_BAMBU_ENTRY_ID,
    CONF_ENERGY_ENTITY,
    CONF_FILAMENT_PRICES,
    CONF_NOTIFY_FILAMENT_LOW,
    CONF_POWER_ENTITY,
    CONF_PRICE_ENTITY,
    CONF_PRICE_PER_KG,
    CONF_PRICE_PER_KWH,
    CONF_SERIAL,
    DEFAULT_FILAMENT_LOW,
    DEFAULT_PRICE_PER_KG,
    DEFAULT_PRICE_PER_KWH,
    DOMAIN,
)
from .history import parse_prices


def _entity_selector(device_class: str | None = None) -> selector.EntitySelector:
    cfg: dict[str, Any] = {"domain": ["sensor", "input_number", "number"]}
    if device_class:
        cfg["device_class"] = device_class
    return selector.EntitySelector(selector.EntitySelectorConfig(**cfg))


def _optional(key: str, defaults: dict[str, Any]) -> vol.Optional:
    value = defaults.get(key)
    if value:
        return vol.Optional(key, description={"suggested_value": value})
    return vol.Optional(key)


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
                    **{
                        k: user_input[k]
                        for k in (CONF_ENERGY_ENTITY, CONF_POWER_ENTITY)
                        if user_input.get(k)
                    },
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
                ),
                vol.Optional(CONF_ENERGY_ENTITY): _entity_selector("energy"),
                vol.Optional(CONF_POWER_ENTITY): _entity_selector("power"),
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
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                parse_prices(user_input.get(CONF_FILAMENT_PRICES))
            except ValueError:
                errors[CONF_FILAMENT_PRICES] = "invalid_prices"
        if user_input is not None and not errors:
            # Cleared optional entities are stored as None so they override the setup data.
            for key in (CONF_ENERGY_ENTITY, CONF_POWER_ENTITY, CONF_PRICE_ENTITY):
                user_input.setdefault(key, None)
            return self.async_create_entry(data=user_input)
        opts = {**self.config_entry.data, **self.config_entry.options}
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_PRICE_PER_KG,
                    default=opts.get(CONF_PRICE_PER_KG, DEFAULT_PRICE_PER_KG),
                ): vol.All(vol.Coerce(float), vol.Range(min=0)),
                vol.Optional(
                    CONF_FILAMENT_PRICES,
                    description={"suggested_value": opts.get(CONF_FILAMENT_PRICES, "")},
                ): selector.TextSelector(selector.TextSelectorConfig(multiline=True)),
                vol.Required(
                    CONF_NOTIFY_FILAMENT_LOW,
                    default=opts.get(CONF_NOTIFY_FILAMENT_LOW, DEFAULT_FILAMENT_LOW),
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
                vol.Required(
                    CONF_AUTO_IMPORT, default=opts.get(CONF_AUTO_IMPORT, True)
                ): bool,
                vol.Required(
                    CONF_PRICE_PER_KWH,
                    default=opts.get(CONF_PRICE_PER_KWH, DEFAULT_PRICE_PER_KWH),
                ): vol.All(vol.Coerce(float), vol.Range(min=0)),
                _optional(CONF_PRICE_ENTITY, opts): _entity_selector(),
                _optional(CONF_ENERGY_ENTITY, opts): _entity_selector("energy"),
                _optional(CONF_POWER_ENTITY, opts): _entity_selector("power"),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
