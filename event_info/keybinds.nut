::EventInfo.Mod.Keybinds.addSQKeybind("toggleDisplayUIScreen", "ctrl+e", ::MSU.Key.State.World, ::EventInfo.EventScreen.toggle.bindenv(::EventInfo.EventScreen), "Open/Close Event Info UI");

::EventInfo.Mod.Keybinds.addSQKeybind("CloseScreen", "escape", ::MSU.Key.State.World, function() {
	::EventInfo.HideUI();
}, "Close Screen", ::MSU.Key.KeyState.Press).setBypassInputDenied(true);

