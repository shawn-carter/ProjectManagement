from django import forms

class DurationPickerWidget(forms.TextInput):
    """
    Custom widget for DurationField to handle inputs like '2 days' or '8 hours'.
    Uses a TextInput to display the duration in a more user-friendly format.
    """
    def __init__(self, attrs=None):
        super().__init__(attrs)
        if not attrs:
            attrs = {}
        attrs['placeholder'] = 'e.g., 2 days, 8 hours'
        self.attrs = attrs

    def format_value(self, value):
        if isinstance(value, (str,)):
            return value
        if value:
            days = value.days
            seconds = value.seconds
            hours = seconds // 3600
            return f"{days} days, {hours} hours"
        return super().format_value(value)