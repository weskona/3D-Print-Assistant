"""Constants for the 3D Print Assistant integration."""

DOMAIN = "druck_assistant"
BAMBU_DOMAIN = "bambu_lab"

CONF_BAMBU_ENTRY_ID = "bambu_entry_id"
CONF_SERIAL = "serial"
CONF_PRICE_PER_KG = "price_per_kg"
CONF_FILAMENT_PRICES = "filament_prices"
CONF_ENERGY_ENTITY = "energy_entity"
CONF_POWER_ENTITY = "power_entity"
CONF_PRICE_PER_KWH = "price_per_kwh"
CONF_PRICE_ENTITY = "price_entity"
CONF_NOTIFY_FILAMENT_LOW = "filament_low_threshold"

DEFAULT_PRICE_PER_KG = 25.0
DEFAULT_FILAMENT_LOW = 15
DEFAULT_PRICE_PER_KWH = 0.30
MAX_HISTORY = 200

STORAGE_VERSION = 1

PANEL_URL_PATH = "druck-assistant"
PANEL_COMPONENT = "druck-assistant-panel"
STATIC_URL = "/druck_assistant_static"
WS_DATA = f"{DOMAIN}/data"
WS_SPOOL_SAVE = f"{DOMAIN}/spool_save"
WS_SPOOL_DELETE = f"{DOMAIN}/spool_delete"
WS_SPOOL_ASSIGN = f"{DOMAIN}/spool_assign"

# Raw print_status values reported by ha-bambulab.
STATUS_RUNNING = "running"
STATUS_PAUSE = "pause"
STATUS_FINISH = "finish"
STATUS_FAILED = "failed"
ACTIVE_STATUSES = {STATUS_RUNNING, STATUS_PAUSE}
END_STATUSES = {STATUS_FINISH, STATUS_FAILED}

EVENT_PRINT_STARTED = f"{DOMAIN}_print_started"
EVENT_PRINT_FINISHED = f"{DOMAIN}_print_finished"
EVENT_PRINT_FAILED = f"{DOMAIN}_print_failed"
EVENT_FILAMENT_LOW = f"{DOMAIN}_filament_low"
