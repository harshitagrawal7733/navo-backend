class PreferencesUtil:
    @staticmethod
    def get_k(preferences, default=3):
        if preferences and isinstance(preferences, dict):
            return preferences.get("k", default)
        return default

    @staticmethod
    def get_tools(preferences):
        if preferences and isinstance(preferences, dict):
            return preferences.get("tool", [])
        return []

    @staticmethod
    def get_role(preferences):
        if preferences and isinstance(preferences, dict):
            return preferences.get("role", "")
        return ""

    @staticmethod
    def get_team(preferences):
        if preferences and isinstance(preferences, dict):
            return preferences.get("team", "")
        return ""

    @staticmethod
    def get_project(preferences):
        if preferences and isinstance(preferences, dict):
            return preferences.get("project", "")
        return ""
