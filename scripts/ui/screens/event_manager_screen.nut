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
		//from world_state.topbar_options_module_onPerksButtonClicked()
		// if (::World.State.m.MenuStack.hasBacksteps() || this.isVisible() || this.isAnimating())
		// {
		// 	//::logWarning("")
		// 	return;
		// }

		// this.setAutoPause(true);
		// this.m.CustomZoom = this.World.getCamera().Zoom;
		// this.World.getCamera().zoomTo(1.0, 4.0);
		// this.Music.setTrackList(this.Const.Music.CampfireTracks, this.Const.Music.CrossFadeTime);
		// this.Tooltip.hide();
		// this.m.WorldScreen.hide();
		// this.m.CampfireScreen.show();
		// this.Cursor.setCursor(this.Const.UI.Cursor.Hand);

		// this.m.MenuStack.push(function ()
		// {
		// 	this.setWorldmapMusic(false);
		// 	this.World.getCamera().zoomTo(this.m.CustomZoom, 4.0);
		// 	this.m.CampfireScreen.hide();
		// 	this.m.WorldScreen.show();
		// 	this.Cursor.setCursor(this.Const.UI.Cursor.Hand);
		// 	this.setAutoPause(false);
		// }, function ()
		// {
		// 	return !this.m.CampfireScreen.isAnimating();
		// });

		//local activeState = ::MSU.Utils.getActiveState();

		//::World.State.onHide();

		::logWarning("show()");

		::World.State.setAutoPause(true);
		//this.Tooltip.hide();
		//::World.State.m.WorldScreen.hide();
		//::World.State.m.CustomZoom = this.World.getCamera().Zoom;


		this.Cursor.setCursor(this.Const.UI.Cursor.Hand);

		::World.State.m.MenuStack.push(function(){
			//::logWarning("MenuStack is now running the code");
			::EventManagerInfo.EventScreen.hide();
			//::World.State.m.WorldScreen.show();
			//this.onShow();
			this.setAutoPause(false);
		});

		local data = this.getUIData();

		this.Tooltip.hide();
		this.m.JSHandle.asyncCall("setData", data);
		this.m.JSHandle.asyncCall("show", null);

		::logWarning("show() UI should be there...");

		return false;



		// if (!this.isVisible())
		// 	{

		// 	}



		// try {


		// 	if (this.isVisible()) {
		// 		return;
		// 	}

		// 	local activeState = ::MSU.Utils.getActiveState();

		// 	if (activeState.ClassName != "world_state")
		// 	{
		// 		::logWarning("The Event Manager will only open in World State");
		// 		return;
		// 	}

		// 	//this.m.PauseState = activeState.m.IsGameAutoPaused;

		// 	activeState.setAutoPause(true);

		// 	local data = this.getUIData();

		// 	activeState.m.MenuStack.push(function(){
		// 		::logWarning("MenuStack is now running the code");

		// 		::EventManagerInfo.EventScreen.hide();
		// 		this.setAutoPause(false);
		// 	});

		// 	//this.ui_screen.show(data);
		// 	this.m.JSHandle.asyncCall("setData", data);
		// 	this.m.JSHandle.asyncCall("show", null);
		// } catch (exception){
		// 	::logError("Error while showing Events UI window. " + exception);
		// }

		// return false;
	}

	function hide()
	{
		if (this.isVisible())
		{
			::logWarning("hide() isVisible()");
			//local activeState = ::MSU.Utils.getActiveState();
			this.m.JSHandle.asyncCall("hide", null);
			::World.State.m.MenuStack.pop();
			//::World.State.m.MenuStack.pop();
			return false;
		}

		::logWarning("hide() is not visible");

		// try {\
		// 	::logInfo("hide() called!");

		// 	if (!this.isVisible()) {
		// 		::logInfo("hide() reported not visible");
		// 		return false;
		// 	}





		// 	//this.ui_screen.hide();



		// 	//activeState.setAutoPause(this.m.PauseState);
		// 	//return false;
		// } catch (exception){
		// 	::logError("Error while hiding Events UI window. " + exception);
		// }

		// return false;
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
