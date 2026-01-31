this.event_manager_screen <- ::inherit("scripts/mods/msu/ui_screen", {
	m = {
		ID = "EventManagerScreen"
	},

	function create()
	{
		this.ui_screen.create();
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
		::World.State.setAutoPause(true);

		this.Cursor.setCursor(this.Const.UI.Cursor.Hand);

		::World.State.m.MenuStack.push(function(){
			::EventManagerInfo.EventScreen.hide();
			this.setAutoPause(false);
		});

		local data = this.getUIData();

		this.Tooltip.hide();
		this.m.JSHandle.asyncCall("setData", data);
		this.m.JSHandle.asyncCall("show", null);

		return false;
	}

	function hide()
	{
		if (this.isVisible())
		{
			this.m.JSHandle.asyncCall("hide", null);
			::World.State.m.MenuStack.pop();
			return false;
		}
	}

	function toggle()
	{
		if(this.m.Animating)
		{
			return false
		}

		this.isVisible() ? this.hide() : this.show();

		return true;
	}

	function onCloseButtonPressed()
	{
		this.hide();
	}
});
