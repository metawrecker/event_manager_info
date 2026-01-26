this.event_manager_screen <- ::inherit("scripts/mods/msu/ui_screen", {
	m = {
		ID = "EventManagerScreen"
	},

	function create()
	{
	}

	function getUIData()
	{
		::EventManagerInfo.Events.processEventsAndStoreValues();

		local ret = {
			BroHireEventsInPool = [],
			NonBroHireEventsInPool = [],
			EventsOnCooldown = [],
			AllScores = 0,
			NonEventBroHireScore = 0,
			EventBroHireScore = 0
		};

		ret.BroHireEventsInPool = ::EventManagerInfo.Events.getBroHiringEventsInQueue();
		ret.NonBroHireEventsInPool = ::EventManagerInfo.Events.getNonBroHiringEventsInQueue();
		ret.EventsOnCooldown = ::EventManagerInfo.Events.getEventsOnCooldown();
		ret.AllScores = ::EventManagerInfo.Events.getAllEventScore();
		ret.NonEventBroHireScore = ::EventManagerInfo.Events.getNonEventBroHiringScore();
		ret.EventBroHireScore = ::EventManagerInfo.Events.getEventBroHiringScore();

		return ret;
	}

	function show()
	{
		try {
			if (this.isVisible()) {
				return;
			}

			local data = this.getUIData();

			this.ui_screen.show(data);
		} catch (exception){
			::logError("Error while showing Events UI window. " + exception);
		}
	}
});
