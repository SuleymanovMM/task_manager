class NotificationNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__("Notification not found")
