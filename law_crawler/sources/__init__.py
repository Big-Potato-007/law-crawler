"""Site-specific search adapters."""

from .gov_cn import GovCnSource

SOURCE_REGISTRY = {
    "gov.cn": GovCnSource(),
}
