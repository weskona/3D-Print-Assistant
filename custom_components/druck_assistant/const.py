"""Constants for the 3D-Druck-Assistant integration."""

DOMAIN = "druck_assistant"
BAMBU_DOMAIN = "bambu_lab"

CONF_BAMBU_ENTRY_ID = "bambu_entry_id"
CONF_SERIAL = "serial"
CONF_PRICE_PER_KG = "price_per_kg"
CONF_NOTIFY_FILAMENT_LOW = "filament_low_threshold"

DEFAULT_PRICE_PER_KG = 25.0
DEFAULT_FILAMENT_LOW = 15
MAX_HISTORY = 200

STORAGE_VERSION = 1

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
