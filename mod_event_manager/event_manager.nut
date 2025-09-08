::mods_hookExactClass("events/event_manager", function (o)
{
	local onSelectEvent = o.selectEvent;
	o.selectEvent = function ()
	{
		onSelectEvent();

		::EventManagerInfo.PrintEventsToLog(false, false);
	}
});