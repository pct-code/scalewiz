LOGGER = getLogger("scalewiz.config")
        LOGGER.info("No config directory found. Making one now at %s", CONFIG_DIR)
        LOGGER.info(
        LOGGER.info("Successfully built a new config file at %s", CONFIG_FILE)
        LOGGER.info("Updated %s.%s to %s", table, key, value)
        LOGGER.info("Failed to update %s.%s to %s", table, key, value)
