class AppContext:
    def __init__(self, page):
        self.page = page
        self.config = {}
        self.is_active = False
        # Callback for adding log messages: function(message, type)
        self.on_message = None 
        # Callback for adding course: function(course_data)
        self.on_add_course = None
        # Callback for deleting course: function(index)
        self.on_del_course = None

    def add_message_signal_emit(self, message, type=0):
        if self.on_message:
            self.on_message(message, type)

    def add_course_signal_emit(self, course_data, index):
        if self.on_add_course:
            self.on_add_course(course_data, index)
            
    def del_course_signal_emit(self, index):
        if self.on_del_course:
            self.on_del_course(index)
            
    # Mimic the Qt signal object
    class Signal:
        def __init__(self, emit_func):
            self.emit = emit_func

    @property
    def add_message_signal(self):
        return self.Signal(self.add_message_signal_emit)
        
    @property
    def add_course_signal(self):
        return self.Signal(self.add_course_signal_emit)
        
    @property
    def del_course_signal(self):
        return self.Signal(self.del_course_signal_emit)

    # Mimic tableWidget.rowCount()
    @property
    def tableWidget(self):
        class Table:
            def __init__(self, ctx):
                self.ctx = ctx
            def rowCount(self):
                # We need to access the actual row count from the UI state
                # For now, return a placeholder or implement a way to get it
                # Since Classes.py calls self.main_ui.tableWidget.rowCount() to determine index
                # We can probably manage course count in AppContext
                return getattr(self.ctx, "course_count", 0)
        return Table(self)
