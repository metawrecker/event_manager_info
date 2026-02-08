foreach (file in ::IO.enumerateFiles("event_info/hooks"))
{
	::include(file);
}

::include("event_info/event_utils");
::include("event_info/keybinds");
::include("event_info/settings");
::include("event_info/toolips");