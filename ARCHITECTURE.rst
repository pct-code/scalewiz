This is a general mapping of the code / code flow 

::

    models/
     data models, dict-like collections of tkinter variables that can serialize themselves as JSON
    ├──  project.py
    │    organizes a collection of Tests with some metadata
    ├──  test.py
    │    organizes a collection of readings for a Test with some metadata
    ╰──  test_handler.py
         not really a 'model' nor a 'component' - collects readings over serial, sticks them in a Test in a Project

     components/
     custom tkinter widgets bundled with a minimum of business logic
    ├──  scalewiz_log_window.py
    │    a tkinter ScrolledText that trampolines on the mainloop to poll logging messages from a Queue
    ├──  scalewiz_rinse_window.py
    │    a small toplevel that can run the pumps for a user-defined duration
    ├──  scalewiz.py
    │    core object of the app, used for setting up logging and ttk styles
    │   ├──  scalewiz_main_frame.py
    │   │    the main frame of the application, holds a notebook widget
    │   ├──  scalewiz_menu_bar.py
    │   │    defines the menu bar that gets loaded on to the main menu
    │   ╰──  handler_view.py
    │        represents a tab within the main frame's notebook
    │       ├──  handler_view_devices_entry.py
    │       │    widget for comboboxes, can poll for COM/serial port devices
    │       ├──  handler_view_info_entry.py
    │       │    widget for user entry of Test metadata
    │       ├──  handler_view_controls.py
    │       │    widget that holds the progess bar, readings log, and start/stop buttons
    │       ╰──  handler_view_plot.py
    │            widget that displays an animated matplotlib plot of the data collected for a running Test
    ├──  project_editor.py
    │    toplevel for making/mutating Projects
    │   ├──  project_editor_info.py
    │   │    form for metadata
    │   ├──  project_editor_params.py
    │   │    form for experiment parameters -- affects how Tests are run and scored
    │   ╰──  project_editor_report.py
    │        form for setting exported report preferences
    ╰──  evaluation_window.py
         toplevel for displaying a Project summary with a notebook widget
        ├──  evaluation_data_view.py
        │    frame that displays a table-like view of data in a Project, giving each Test a row
        ╰──  evaluation_plot_view.py
             frame that uses matplotlib to plot a selection of data

     helpers/
     helper functions that didn't fit elsewhere
    ├──  configuration.py
    │    handles read/writing a config TOML file
    ├──  score.py
    │    modifies a Project by calculating and assigning a score for each Test, optionally sending a log to a text widget
    ├──  export.py
    │    handles exporting a summary of a Project to an output (JSON, CSV, etc.)
    ├──  show_help.py
    │    opens a link to the documentation in a browser window
    ├──  sort_nicely.py
    │    does some pleasant sorting -- used when sorting Tests within a Project
    ├──  validation.py
    │    some functions used for validation in entry widgets
    ├──  set_icon.py
    │    sets the icon of a toplevel widget
    ╰──  get_resource.py
         fetches a file

     main thread -- tkinter mainloop, performs UI updates
     can spawn an arbitrary number of TestHandlers/RinseWindows, each with child threads as follows
    ├──  TestHandler's data collection thread -- alive only while a Test is running
    │    collects readings on a blocking loop
    │   ╰──  2 data collection threads
    │        one for each pump -- performs a quick (~30ms) I/O and returns
    ├──  RinseWindow's thread
    │    the rinse window can spawn a thread IFF the TestHandler isn't running a Test
    ╰──  ...
    
    
    
.. image:: ../img/architecture.PNG
    :alt: code graph
    
