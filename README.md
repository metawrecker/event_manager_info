## Event Info
I created this Battle Brothers mod because the entire event system in the game is a black box. Someone did add events to the Battle Brothers Fandom wiki but the searching method is cumbersome and it's a large undertaking to try to figure out what events you qualify for at any given time of your run. 
- This mod was written with a special focus on Event Brother events; namely events that may reward a brother to your company. But, if you are trying to qualify for a different event, you can use this mod for that purpose as well.
- This mod uses the in-game Event Manager, so the events available and the events on cooldown are the exact values stored in the Event Manager.

### How does it it work?

- Behind the scenes, there is an Event Manager that tracks all of the 400 or so in-game events.
- Every 3-4 in-game days (on average), an event will 'fire' or appear on screen.
- Every event has one or more logic check that must pass in order for the event to qualify for the event pool.
- Each event has a 'score' value. 
- The event pool is like a raffle ticket system. The sum of all events in the pool make up the total number of 'points' and each event 'score' holds the number of tickets that hold that event. (i.e., the Belly Dancer event has a score of 15, so imagine it has 15 raffle tickets in the 'hat'.)
- When an event is going to 'fire', a random value between 1 and the max event pool 'score' is selected. Then, the Event Manager cycles through the events in the pool subtracting each event's score until the event being evaluated falls in the number that was originally selected.
- Once an event fires, it is on cooldown based on the Cooldown setting assigned to the event.

### Example
- Pretend there are 5 events in the pool: 
- Event 1 for 10 score.
- Event 2 for 5 score. 
- Event 3 for 10 score.
- Event 4 for 25 score.
- Event 5 for 5 score.
- With those 5 events, the event pool has a total score of 55 points.
- Imagine the Event Manager rolls a random value of 26.
- When an event is going to fire, the Event Manager processes events from start to finish. I.e., event 1, event 2. etc.
- Event Manager then cycles through the events:
- Cycle 1 evaluates Event 1, which includes scores 1-10. That range does not include 26, so skip.
- Cycle 2 evaluates Event 2, which includes scores 11-15. That range does not include 26, so skip.
- Cycle 3 evaluates Event 3, which includes scores 16-25. That range does not include 26, so skip.
- Cycle 4 evaluates Event 4, which includes scores 26-50. That range does include 26. Fire this event.
- Event 4 is now on Cooldown.

## Features
Event Pool
-    All events that you currently qualify for will appear here. Brother and Dog events get fun extra icons.

![20260225150640_1](https://github.com/user-attachments/assets/07a6e899-0dbc-436a-b8eb-2adb202b6124)

On Cooldown
-    All events that are on cooldown, sorted from smallest to largest "Fired On Day" value.

![20260225150653_1](https://github.com/user-attachments/assets/8befda97-9a8a-4ea6-b640-5faba6bd43e9)

### Does this mod change vanilla behavior?
- There are NO code changes to how vanilla's event system works. This is an 'info only' mod.

### How does it work?
- Press Ctrl+e to open the events popup window. Press Ctrl+e or Esc to close the window. You can change these keybinds in the Mod Settings folder.
- Explore the MSU Mod Settings menu for settings that impact the filters and crises event masking.

![20260225150707_1](https://github.com/user-attachments/assets/5f540cf7-083f-4799-be72-c662d76cfd1f)

### Pre-requisites
- Modding Standards & Utilities 1.3.0 and higher
- Modern Hooks 0.4.10 or higher

### Compatability
- You can add or remove this mod anytime
- Mods that modify event coolsdowns or add new events may not work if those mods don't properly update the Event Manager. 
