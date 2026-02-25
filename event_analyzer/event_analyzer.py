#!/usr/bin/env python3

import re
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

class EventAnalyzer:
    def __init__(self):
        self.reset()

    def reset(self):
        self.content = ""

        self.data = {
            'UnhandledLines': [],

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
            'RequiredOrigins': [],
            'ExcludedOrigins': [],
            'RequiredCrises': None,
            'MinimumDays': None,
            'MaximumDays': None,
            'NumberOfEmptyInventorySlots': None
        }
        
        self.current_event_id = None
        self.iterates_through_roster = False
        self.town_match = False

        self.dlc_map = {
            "Lindwurm": "Lindwurm",
            "Unhold": "Beasts & Exploration",
            "Wildmen": "Warriors Of The North",
            "Desert": "Blazing Deserts",
            "Paladins": "Of Flesh And Faith"
        }

        self.crises_map = {
            "isHolyWar": "Holy War",
            "isCivilWar": "Noble War",
            "isGreenskinInvasion": "Greenskin Invasion",
            "isUndeadScourge": "Undead Invasion"
        }

    def analyze_directory(self, directory: str, output_file: str = 'event_requirements.nut'):
        results = []
        
        event_dir = Path(directory)
        if not event_dir.exists():
            print(f"Error: Directory '{directory}' does not exist", file=sys.stderr)
            return
        
        nut_files = list(event_dir.rglob('*.nut'))
        print(f"Found {len(nut_files)} .nut files")

        analyzer = EventAnalyzer()
        
        for i, filepath in enumerate(nut_files, 1):
            if i % 50 == 0:
                print(f"Processing {i}/{len(nut_files)}...")
            
            result = analyzer.analyze_file(str(filepath))
            if result:
                #print(result)
                results.append(result)

        print(f"\nAnalyzed {len(results)} event files with requirements")

        #print(results)
        
        generate_squirrel_file(results, output_file)
        print(f"Generated {output_file}")

    def analyze_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)
            return None
        
        if self.file_should_not_be_processed(content):
            return None
        
        if self.file_is_for_a_special_event(content):
            return None
        
        # Reset for new file
        self.reset()

        self.data['FileName'] = os.path.basename(filepath)
        self.data['EventID'] = self.extract_event_id(content)
        self.current_event_id = self.data['EventID']

        on_update_score = self.extract_function(content, 'onUpdateScore')
        if not on_update_score:
            return None
        
        self.content = on_update_score

        self.analyze_function(on_update_score)

        #Clean up - remove None values
        result = {}
        for k, v in self.data.items():
            if v is not None and v != []:
                result[k] = v

        # if 'EventID' not in result:
        #     result['EventID'] = self.data['EventID']
        # if 'FileName' not in result:
        #     result['FileName'] = self.data['FileName']
        
        return result if len(result) > 1 else None
    
    def file_should_not_be_processed(self, content: str) -> bool:
        if 'onUpdateScore' not in content:
            return True
        return False

    def file_is_for_a_special_event(self, content: str) -> bool:
        if 'this.m.IsSpecial = true;' in content:
            return True
        return False
    
    def extract_event_id(self, content: str) -> str:
        match = re.search(r'this\.m\.ID\s*=\s*"([^"]+)"', content)
        if match:
            print(match.group(1))
            return match.group(1)
        
        return "unknown"
    
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
    
    def get_if_block_contents(self, if_line) -> Optional[str]:
        if not self.content:
            print("onUpdateScore() function not found")
            return None
        
        lines = self.content.split('\n')
        
        # Find the index of the if statement line
        if_index = None
        for i, line in enumerate(lines):
            if if_line in line.strip():
                if_index = i
                break
        
        if if_index is None:
            print("if_index is None")
            return None

        # Find the opening brace
        brace_index = None
        for i in range(if_index, len(lines)):
            if '{' in lines[i]:
                brace_index = i
                break

        if brace_index is None:
            print("brace_index is None")
            return None

        # Collect lines until closing brace
        contents = []
        for i in range(brace_index + 1, len(lines)):
            if '}' in lines[i]:
                break
            contents.append(lines[i].strip())

        return '\n'.join(contents)
    
    def analyze_function(self, func_body: str):
        lines = func_body.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()

            if not self._line_should_be_evaluated(line):
                continue
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
            if self._line_is_for_day_check(line):
                continue
            if self._line_is_for_inventory_check(line):
                continue

            self.data['UnhandledLines'].append(line)

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
    
    def _line_is_for_tile_check(self, line: str) -> bool:
        matched_location = False
        tileDetails = {}

        if 'isSouthern()' in line:
            self.data['SettlementType'] = "Southern"
            matched_location = True

        if 't.hasSituation("situation.arena_tournament"' in line:
            print("NEED TO HANDLE t.hasSituation('situation.arena_tournament')")

        if 'getTile().getDistanceTo' in line:
            match = re.search(r'getDistanceTo.*?([<>=!]+)\s*(\d+)', line)

            if match:
                matched_location = True
                operator = match.group(1)
                distance = int(match.group(2))

                if_statement_contents = self.get_if_block_contents(line)

                if if_statement_contents is None:
                    matched_location = False
                else:
                    if 'return' in if_statement_contents:
                        if '>=' in operator:
                            self.data['MaxDistanceFromSettlement'] = distance + 1
                        elif '<=' in operator:
                            self.data['MinDistanceFromSettlement'] = distance + 1
                        elif '>' in operator:
                            self.data['MaxDistanceFromSettlement'] = distance
                        elif '<' in operator:
                            self.data['MinDistanceFromSettlement'] = distance
                    if 'break;' in if_statement_contents:
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
            matched_location = True
            self.data['SettlementMustNotBeHostile'] = False

        if '!currentTile.HasRoad' in line or '!currentTile.HasRoad' in line:
            matched_location = True
            tileDetails["Road"] = "OnRoad"
        elif 'currentTile.HasRoad' in line or 'currentTile.HasRoad' in line:
            matched_location = True
            tileDetails["Road"] = "OffRoad"

        if 'currentTile.Type' in line:
            match = re.search(r'([\w.]+)\s*(==|!=)\s*this\.Const\.World\.TerrainType\.(\w+)', line)

            if match:
                matched_location = True
                operator = match.group(2)
                terrainType = match.group(3)

                if '!=' in operator:
                    tileDetails["TerrainType"] = terrainType

        if 'currentTile.TacticalType' in line:
            match = re.search(r'([\w.]+)\s*(==|!=)\s*this\.Const\.World\.TerrainTacticalType\.(\w+)', line)

            if match:
                matched_location = True
                operator = match.group(2)
                tactical_type = match.group(3)

                if '!=' in operator:
                    tileDetails["TacticalType"] = tactical_type

        # currentTile.SquareCoords.Y > this.World.getMapSize().Y * 0.7
        if "SquareCoords" in line and "getMapSize()" in line:
            match = re.search(r'([<>=!]+)\s*this\.World\.getMapSize\(\)\.Y\s*\*\s*(\d+\.\d+)', line)

            if match:
                matched_location = True
                operator = match.group(1)
                y_value = float(match.group(2))
                y_percent = int(y_value * 100)

                if ">=" in operator:
                    tileDetails["OnOrBelowYLine"] = y_percent
                elif "<=" in operator:
                    tileDetails["OnOrAboveYLine"] = y_percent
                elif ">" in operator:
                    tileDetails["BelowYLine"] = y_percent
                elif "<" in operator:
                    tileDetails["AboveYLine"] = y_percent

        if tileDetails:
            if self.data['TileRequirements'] is not None:
                self.data['TileRequirements'].update(tileDetails)
            else:
                self.data['TileRequirements'] = tileDetails

        return matched_location
    
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

                if "==" in operator:
                    self.data['ExcludedOrigins'].append(origin)
                elif "!=" in operator:
                    self.data['RequiredOrigins'].append(origin)
                #self.data['OriginRequirements'].append({"origin": origin, "operator": operator})

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
    
    def _line_is_for_day_check(self, line: str) -> bool:
        if 'getTime()' not in line: 
            return False
        
        match = re.search(r'getTime\(\)\.Days\s*([<>=!]+)\s*(\d+)', line)
        
        #this.World.getTime().Days > 10
        if match:
            operator = match.group(1)
            days = int(match.group(2))

            if '<' in operator:
                self.data['MinimumDays'] = days + 1
            elif '<=' in operator:
                self.data['MinimumDays'] = days
            elif '>' in operator:
                self.data['MaximumDays'] = days + 1
            elif '>=' in operator:
                self.data['MaximumDays'] = days
        
            return True

        return False
    
    def _line_is_for_inventory_check(self, line: str) -> bool:
        if 'getStash()' not in line: 
            return False

        #'if (!this.World.Assets.getStash().hasEmptySlot())'
        match = re.search(r'if\s*\(\s*(!?)\s*this\.World\.Assets\.getStash\(\)\.hasEmptySlot\(\)\)', line)

        if match:
            if '!' in match.group(1):
                self.data['NumberOfEmptyInventorySlots'] = 1

            return True
        
        #"if (this.World.Assets.getStash().getNumberOfEmptySlots() < 1)"
        match = re.search(r'getStash\(\)\.getNumberOfEmptySlots\(\)\s*([<>=!]+)\s*(\d+)', line)
        
        if match:
            operator = match.group(1)
            slots = int(match.group(2))

            if '<' in operator or '<=' in operator:
                self.data['NumberOfEmptyInventorySlots'] = slots
            elif '>' in operator:
                self.data['NumberOfEmptyInventorySlots'] = slots + 1
            elif '>=' in operator:
                self.data['NumberOfEmptyInventorySlots'] = slots
        
            return True
        
        return False


def generate_squirrel_file(events: List[Dict[str, Any]], output_file: str):
    lines = [
        "// Battle Brothers Event Requirements Database",
        f"// Total events: {len(events)}",
        "",
        "this.EventRequirements <- [",
    ]
    
    for i, event in enumerate(events):
        lines.append("    {")
        
        for key, value in sorted(event.items()):
            squirrel_value = convert_python_to_squirrel(value)
            lines.append(f"        {key} = {squirrel_value},")
        
        if i < len(events) - 1:
            lines.append("    },")
        else:
            lines.append("    }")
        
        #lines.append("")
    
    lines.append("];")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def convert_python_to_squirrel(value):
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        return str(value)
    elif isinstance(value, str):
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    elif isinstance(value, dict):
        if not value:
            return "{}"
        items = []
        for k, v in value.items():
            squirrel_val = convert_python_to_squirrel(v)
            items.append(f"{k} = {squirrel_val}")
        return "{ " + ", ".join(items) + " }"
    elif isinstance(value, list):
        if not value:
            return "[]"
        items = [convert_python_to_squirrel(item) for item in value]
        return "[" + ", ".join(items) + "]"
    return "null"

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python analyze_bb_events_v3.py <path_to_events_directory> [output_file.nut]")
        sys.exit(1)
    
    events_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'event_requirements.nut'
    
    #tracker = PatternTracker()
    analyzer = EventAnalyzer()
    analyzer.analyze_directory(events_dir, output_file)