::EventManagerInfo <- {
	ID = "mod_event_manager_info",
	Name = "Event Manager Info",
	Version = "0.9.5"
}

/*
	To do
	. Top buttons need to stay selected (done)
	. Make filter work (done)
	. Fix button to align center (done??)
	. Adjust section borders maybe (done)
	. Add checkbox to highlight or show only bro events in both queue and cooldown (done)
	. Fix "no events found" firing when there is clearly content.. (skip)
	. Center Message (skip)
	. Fix on cooldown sorting (done)
	. Mark events as bro events in some way (done)
	. Add logic to filter out non - valid bro events(done)
	. Fill in DestroyDIV()
	. Reset form on hide()

	. Investigate more readable day numbers (especially with rounding!)
	. Add logic to process events in the cooldown list
	. Fix grid header and content alignment
	. Fix defaulting to hiding 9999 cooldown events not working
	. Fix show() and hide() not resetting the UI back to first state

*/

local requiredMods = [
	"vanilla >= 1.5.1-6",
	"mod_msu >= 1.3.0",
	"mod_modern_hooks >= 0.4.10"
];

local modLoadOrder = [];
foreach (mod in requiredMods) {
	local idx = mod.find(" ");
	modLoadOrder.push(">" + (idx == null ? mod : mod.slice(0, idx)));
}

::EventManagerInfo.HooksMod <- ::Hooks.register(::EventManagerInfo.ID, ::EventManagerInfo.Version, ::EventManagerInfo.Name);
::EventManagerInfo.HooksMod.require(requiredMods);

::EventManagerInfo.HooksMod.queue(modLoadOrder, function() {
 	local mod = ::MSU.Class.Mod(::EventManagerInfo.ID, ::EventManagerInfo.Version, ::EventManagerInfo.Name);
	::EventManagerInfo.Mod <- mod;

	::EventManagerInfo.DisplayEventsInUI <- function()
	{
		::EventManagerInfo.EventScreen.show();
	}

	::include("event_manager/file_loading");

	::Hooks.registerJS("ui/mods/event_manager/event_manager_screen.js");
	::Hooks.registerCSS("ui/mods/event_manager/event_manager_screen.css");

	::EventManagerInfo.EventScreen <- ::new("scripts/ui/screens/event_manager_screen");

	::MSU.UI.registerConnection(::EventManagerInfo.EventScreen);
});