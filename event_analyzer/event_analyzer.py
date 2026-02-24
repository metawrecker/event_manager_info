#!/usr/bin/env python3

import re
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import Counter

class PatternTracker:
    # """Tracks patterns found in event code for reporting"""
    
    def __init__(self):
        self.method_calls = Counter()  # Track all method calls
        self.comparisons = Counter()   # Track comparison patterns
        self.member_accesses = Counter()  # Track property accesses
        self.unhandled_patterns = []   # Patterns we don't handle
        self.warnings = []  # Warnings about potentially missed logic
        
    def add_method_call(self, method: str):
        # """Track a method call"""
        self.method_calls[method] += 1
    
    def add_comparison(self, pattern: str):
        # """Track a comparison pattern"""
        self.comparisons[pattern] += 1
    
    def add_member_access(self, member: str):
        # """Track a property access"""
        self.member_accesses[member] += 1
    
    def add_unhandled(self, pattern: str, context: str = ""):
        # """Track an unhandled pattern"""
        self.unhandled_patterns.append({
            'pattern': pattern,
            'context': context
        })
    
    def add_warning(self, message: str, line: str = "", event_id: str = ""):
        # """Add a warning about potentially missed logic"""
        self.warnings.append({
            'message': message,
            'line': line,
            'event_id': event_id
        })

class EventAnalyzer:
    def __init__(self, pattern_tracker: PatternTracker):
        self.pattern_tracker = pattern_tracker
        self.reset()

    def reset(self):
        self.data = {
            'EventID': None,
            'FileName': None,
            'RequiredDLC': None,
            'TimeOfDay': None,
            'MustHaveOpenRosterSpace': None,
            'MininumCrowns': None,
            'MinDistanceFromSettlement': None,
            'MaxDistanceFromSettlement': None,
            'SettlementType': None, #Southern, Northern T1-T2-T3-Military-NonMilitary
            'SettlementMustNotBeHostile': None,
            'TileRequirements': None,
            'BackgroundRequirements': [],
            'OriginRequirements': [],
            'RequiredCrises': None,
        }
        
        self.current_event_id = None
        self.iterates_through_roster = False
       # self.storesCandidates = False

        self.dlc_map = {
            "Lindwurm": "Lindwurm",
            "Unhold": "Beasts & Exploration",
            "Wildmen": "Warriors Of The North",
            "Desert": "Blazing Deserts",
            "Paladins": "Of Flesh And Faith"
        }

#if 'isHolyWar()' not in line and 'isCivilWar()' not in line and 'isGreenskinInvasion()' not in line and 'isUndeadScourge()' not in line:
        self.crises_map = {
            "isHolyWar": "Holy War",
            "isCivilWar": "Noble War",
            "isGreenskinInvasion": "Greenskin Invasion",
            "isUndeadScourge": "Undead Invasion"
        }

    def analyze_directory(self, directory: str, output_file: str = 'event_requirements.nut'):
        tracker = PatternTracker()
        results = []
        
        event_dir = Path(directory)
        if not event_dir.exists():
            print(f"Error: Directory '{directory}' does not exist", file=sys.stderr)
            return
        
        nut_files = list(event_dir.rglob('*.nut'))
        print(f"Found {len(nut_files)} .nut files")
        
        for i, filepath in enumerate(nut_files, 1):
            if i % 50 == 0:
                print(f"Processing {i}/{len(nut_files)}...")
            
            analyzer = EventAnalyzer(tracker)
            result = analyzer.analyze_file(str(filepath))
            if result:
                print(result)
                results.append(result)
        
        #print(f"\nAnalyzed {len(results)} event files with requirements")
        
        # Generate Squirrel file
        #generate_squirrel_file(results, output_file)
        #print(f"Generated {output_file}")
        
        # Generate analysis report
        #report_file = output_file.replace('.nut', '_analysis_report.txt')
        #generate_analysis_report(tracker, report_file)
        #print(f"Generated {report_file}")
        
        # Print statistics
        #print("\n=== STATISTICS ===")
        # money_events = sum(1 for e in results if 'MinimumCrowns' in e or 'MaximumCrowns' in e)
        # print(f"Events with money requirements: {money_events}")
        
        # roster_events = sum(1 for e in results if 'MinimumBrothers' in e or 'MaximumBrothers' in e)
        # print(f"Events with roster requirements: {roster_events}")
        
        # background_events = sum(1 for e in results if 'RequiredBackgrounds' in e and len(e['RequiredBackgrounds']) > 0)
        # print(f"Events with background requirements: {background_events}")
        
        print(f"\nUnique method calls found: {len(tracker.method_calls)}")
        print(f"Unique comparisons found: {len(tracker.comparisons)}")
        print(f"Total warnings: {len(tracker.warnings)}")
        
        #print(f"\n⚠️  CHECK {report_file} for unhandled patterns!")

    def analyze_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Analyze a single event .nut file"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)
            return None
        
        # Check if this is an event file
        if 'onUpdateScore' not in content:
            return None
        
        if self.event_is_a_special_event(content):
            return None
        
        # Reset for new file
        self.reset()
        
        # Extract metadata
        self.data['FileName'] = os.path.basename(filepath)
        self.data['EventID'] = self.extract_event_id(content)
        self.current_event_id = self.data['EventID']

        # Extract and analyze onUpdateScore function
        on_update_score = self.extract_function(content, 'onUpdateScore')
        if not on_update_score:
            return None
        
        # Analyze the function
        self.analyze_function(on_update_score)

        #print(self.data)
        
        # Store warnings from this event
        # if self.data['_Warnings']:
        #     for warning in self.data['_Warnings']:
        #         self.pattern_tracker.add_warning(
        #             warning['message'],
        #             warning.get('line', ''),
        #             self.current_event_id
        #         )
        
        #Clean up - remove None values and internal tracking
        result = {}
        for k, v in self.data.items():
            if k.startswith('_'):
                continue  # Skip internal tracking fields
            if v is not None and v != [] and v != False:
                result[k] = v
        
        # Always include EventID and FileName
        if 'EventID' not in result:
            result['EventID'] = self.data['EventID']
        if 'FileName' not in result:
            result['FileName'] = self.data['FileName']
        
        return result if len(result) > 2 else None
    
    def extract_event_id(self, content: str) -> str:
        match = re.search(r'this\.m\.ID\s*=\s*"([^"]+)"', content)
        if match:
            print(match.group(1))
            return match.group(1)
        
        return "unknown"
    
    def event_is_a_special_event(self, content: str) -> bool:
        if 'this.m.IsSpecial = true;' in content:
            return True
        return False
    
    def extract_function(self, content: str, func_name: str) -> Optional[str]:
        pattern = rf'function\s+{func_name}\s*\([^)]*\)\s*{{'
        match = re.search(pattern, content)
        if not match:
            return None
        
        start = match.end() - 1
        brace_count = 0
        i = start
        while i < len(content):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return content[start:i+1]
            i += 1
        
        return None
    
    def analyze_function(self, func_body: str):
        lines = func_body.split('\n')
        
        #in_settlement_block = False
        
        for i, line in enumerate(lines):
            line = line.strip()

            if not self._line_should_be_evaluated(line):
                continue

            # print(line)
            
            # Track all method calls and property accesses for reporting
            # self._track_patterns(line)
            
            # Check for settlement block markers
            # if 'nearTown' in line or 'getSettlements' in line:
            #     in_settlement_block = True
            
            # Analyze with existing handlers
            handled = False

            if self._line_is_for_DLC_check(line):
                continue

            if self._line_is_for_time_of_day_check(line):
                continue
        
            if self._line_is_for_open_roster_check(line):
                continue

            if self._line_is_for_money_check(line):
                continue

            if self._line_is_for_tile_check(line):
                continue

            if self._line_is_for_brother_background_check(line):
                continue

            if self._line_is_for_origin_check(line):
                continue

            if self._line_is_for_crises_event(line):
                continue

            # # Check for potentially unhandled logic
            # self._check_for_unhandled_logic(line, handled)

            if not handled:
                print(line)

    def _line_should_be_evaluated(self, line: str) -> bool:
        if not line:
            return False

        if line.find('//') != -1:
            return False
        
        if len(line) < 4:
            return False
        
        if 'this.World.getPlayerRoster().getAll()' in line:
            self.iterates_through_roster = True
            return False
        
        # if 'local candidates = [];' in line:
        #     # set flag...
        #     return False
        
        if line.startswith('local ') or line.startswith('return'):
            return False
        
        if '{' in line or '}' in line:
            return False
        
        if 'if (this.m.Town == null)' in line:
            return False
        
        # if 'candidates' in line:
        #     return False
        
        match = re.search(r'if\s*\(', line)

        if not match:
            return False
    
        return True
    
    def _line_is_for_DLC_check(self, line: str) -> bool:
        if 'Const.DLC' not in line:
            return False
        
        match = re.search(r'if\s*\(\s*(!?)\s*this\.Const\.DLC\.(\w+)\s*\)', line)

        if match:
            boolCheck = match.group(1)
            dlc = match.group(2)

            # if (!this.Const.DLC.Desert) .. return false .. no event score
            if boolCheck == "!":
                self.data["RequiredDLC"] = self.dlc_map[dlc]

            return True

        return False        

    def _line_is_for_time_of_day_check(self, line: str) -> bool:
        if 'getTime()' not in line:
            return False

        match = re.search(r'if\s*\(\s*(!?)\s*this\.World\.getTime\(\)\.IsDaytime\)', line)

        if match:
            boolCheck = match.group(1)

            # if ([!]this.World.getTime().IsDaytime) ... return
            if boolCheck == "!":
                self.data["TimeOfDay"] = "Day"
            else:
                self.data["TimeOfDay"] = "Night"

            return True

        return False
    
    def _line_is_for_open_roster_check(self, line: str) -> bool:
        if 'getPlayerRoster().getSize()' not in line:
            return False
        
        match = re.search(r'(>=|<=|>|<|==|!=)', line)
        if match:
            operator = match.group(1)
            # size = int(match.group(2))

            if '>=' in operator:
                self.data['MustHaveOpenRosterSpace'] = True
            
            return True
            
            # if '<=' in operator:
            #     self.data['MinimumBrothers'] = size
            # elif '>=' in operator:
            #     self.data['MaximumBrothers'] = size
            # elif '<' in operator and '<=' not in operator:
            #     self.data['MinimumBrothers'] = size
            # elif '>' in operator and '>=' not in operator:
            #     self.data['MaximumBrothers'] = size
            # return True

        return False
    
    	# 	if (this.World.Assets.getMoney() < 750)
		# {
		# 	return;
		# }
    
    def _line_is_for_money_check(self, line: str) -> bool:
        if 'getMoney()' not in line:
            return False
        
        match = re.search(r'getMoney\(\)\s*([<>=!]+)\s*(\d+)', line)
        
        if match:
            operator = match.group(1)
            amount = int(match.group(2))
            
            if '<=' in operator:
                self.data['MinimumCrowns'] = amount
            elif '<' in operator:
                self.data['MinimumCrowns'] = amount + 1
            return True
        
        return False
    
    		# 	if (t.isSouthern() && t.getTile().getDistanceTo(currentTile) <= 4 && t.isAlliedWithPlayer())
			# {
			# 	this.m.Town = t;
			# 	break;
			# }
    
    def _line_is_for_tile_check(self, line: str) -> bool:
        matchedLocation = False
        tileDetails = {}

        if 'isSouthern()' in line:
            self.data['SettlementType'] = "Southern"
            matchedLocation = True

        if 'getTile().getDistanceTo' in line:
            match = re.search(r'getDistanceTo.*?([<>=!]+)\s*(\d+)', line)

            if match:
                matchedLocation = True
                operator = match.group(1)
                distance = int(match.group(2))

                if '>=' in operator:
                    self.data['MinDistanceFromSettlement'] = distance
                elif '<=' in operator:
                    self.data['MaxDistanceFromSettlement'] = distance
                elif '>' in operator:
                    self.data['MinDistanceFromSettlement'] = distance + 1
                elif '<' in operator:
                    self.data['MaxDistanceFromSettlement'] = distance + 1

        # MustNotBeHostile is almost always going to be true, only evaluate for false
        if '!isAlliedWithPlayer()' in line:
            matchedLocation = True
            self.data['SettlementMustNotBeHostile'] = False

        if '!currentTile.HasRoad' in line or '!currentTile.HasRoad' in line:
            matchedLocation = True
            tileDetails["Road"] = "OnRoad"
        elif 'currentTile.HasRoad' in line or 'currentTile.HasRoad' in line:
            matchedLocation = True
            tileDetails["Road"] = "OffRoad"

        if 'currentTile.Type' in line:
            match = re.search(r'([\w.]+)\s*(==|!=)\s*this\.Const\.World\.TerrainType\.(\w+)', line)

            if match:
                matchedLocation = True
                operator = match.group(2)
                terrainType = match.group(3)

                if '!=' in operator:
                    tileDetails["TerrainType"] = terrainType

        if 'currentTile.TacticalType' in line:
            match = re.search(r'([\w.]+)\s*(==|!=)\s*this\.Const\.World\.TerrainTacticalType\.(\w+)', line)

            if match:
                matchedLocation = True
                operator = match.group(2)
                tacticalType = match.group(3)

                if '!=' in operator:
                    tileDetails["TacticalType"] = tacticalType


        if tileDetails:
            if self.data['TileRequirements'] is not None:
                self.data['TileRequirements'].update(tileDetails)
            else:
                self.data['TileRequirements'] = tileDetails

        return matchedLocation
    
    def _line_is_for_brother_background_check(self, line: str) -> bool:
        if 'getBackground().getID()' not in line:
            return False

        if 'getLevel()' not in line: 
            matches = re.findall(r'getBackground\(\)\.getID\(\)\s*(==|!=)\s*"([^"]+)"', line)

            if matches:
                for match in matches:
                    operator = match[0]
                    background_str = match[1]
                
                    background_name = background_str.replace('background.', '')
                    if "==" in operator and background_name not in self.data['BackgroundRequirements']:
                        self.data['BackgroundRequirements'].append({"background": background_name, "minLevel": 0, "maxLevel": 0})

                return True
        else:
            if line.index('getBackground()') < line.index('getLevel()'):
                matches = re.findall(r'(==|!=)\s*"([\w.]+)".*?bro\.getLevel\(\)\s*(>=|<=|>|<|==|!=)\s*(\d+)', line)

                if matches:
                    for match in matches:
                        bkgrnd_operator = match[0]
                        background_str = match[1]
                        level_operator = match[2]
                        level = int(match[3])

                       # print("Data: " + background_str + " " + level_operator + match[3])

                        if '==' in bkgrnd_operator:
                            min_level = 0
                            max_level = 0

                            if '>=' in level_operator:
                                min_level = level
                            elif '>' in level_operator:
                                min_level = level + 1
                            elif '<=' in level_operator:
                                max_level = level
                            elif '<' in level_operator:
                                max_level = level - 1

                            background_name = background_name = background_str.replace('background.', '')
                            self.data['BackgroundRequirements'].append({"background": background_name, "minLevel": min_level, "maxLevel": max_level})

                return True
            else:
                matches = re.findall(r'bro\.getLevel\(\)\s*(>=|<=|>|<|==|!=)\s*(\d+).*?(==|!=)\s*"([\w.]+)"', line)

                if matches:
                    for match in matches:
                        bkgrnd_operator = match[2]
                        background_str = match[3]
                        level_operator = match[0]
                        level = int(match[1])

                        if '==' in bkgrnd_operator:
                            min_level = 0
                            max_level = 0

                            if '>=' in level_operator:
                                min_level = level
                            elif '>' in level_operator:
                                min_level = level + 1
                            elif '<=' in level_operator:
                                max_level = level
                            elif '<' in level_operator:
                                max_level = level - 1

                            background_name = background_name = background_str.replace('background.', '')
                            self.data['BackgroundRequirements'].append({"background": background_name, "minLevel": min_level, "maxLevel": max_level})

                return True
        return False

    def _line_is_for_origin_check(self, line: str) -> bool:
        #if (this.World.Assets.getOrigin().getID() != "scenario.gladiators")
        if 'getOrigin().getID()' not in line:
            return False
        
        matches = re.findall(r'(==|!=)\s*"([\w.]+)', line)

        if matches:
            for match in matches:
                #print(match)
                operator = match[0]
                origin_str = match[1]

                origin = origin_str.replace('origin.', '')
                self.data['OriginRequirements'].append({"origin": origin, "operator": operator})

            return True
        return False

    def _line_is_for_crises_event(self, line: str) -> bool:
        if ('isHolyWar()' not in line and 'isCivilWar()' not in line 
            and 'isGreenskinInvasion()' not in line and 'isUndeadScourge()' not in line
            and 'getGreaterEvilType()' not in line):
            return False
        
        if 'getGreaterEvilType()' not in line:
            match = re.search(r'(!?)\s*this\.World\.FactionManager\.(\w+)\(\)', line)

            if match:
                boolCheck = match.group(1)
                crises = match.group(2)

                # if (!this.World.FactionManager.isHolyWar())
                if boolCheck == "!":
                    self.data["RequiredCrises"] = self.crises_map[crises] 
                
                return True
            
        else:
            # build out the logic for 
            # if (this.World.FactionManager.getGreaterEvilType() == this.Const.World.GreaterEvilType.HolyWar 
            # && this.World.FactionManager.getGreaterEvilPhase() == this.Const.World.GreaterEvilPhase.Warning)
            return False

        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python analyze_bb_events_v3.py <path_to_events_directory> [output_file.nut]")
        sys.exit(1)
    
    events_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'event_requirements.nut'
    
    tracker = PatternTracker()
    analyzer = EventAnalyzer(tracker)
    analyzer.analyze_directory(events_dir, output_file)