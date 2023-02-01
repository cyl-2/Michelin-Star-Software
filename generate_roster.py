import random
import json 
#print(json.loads(json.dumps([1,2,3,4])))
class Roster():
    def generate(self, requirements, employees):
        roster = {'mon': {}, 'tue':{}, 'wed':{}, 'thu':{}, 'fri':{}, 'sat':{}, 'sun':{}}
        for day in requirements:
            random.shuffle(employees)
            if day['closing_time'] - day['opening_time'] <= 8:
                for employee in employees:
                    if (
                        str(day['opening_time'])+":00-"+str(day['closing_time'])+":00" not in roster[day['day']] or 
                        len(roster[day['day']][str(day['opening_time'])+":00-"+str(day['closing_time'])+":00" ]) < day['min_workers']
                        ): 
                            if employee not in json.loads(day['unavailable']):
                                working = 0
                                for workday in roster:# check employee has less than 6 days 
                                    for value in roster[workday].values():
                                        if employee in value:
                                            working += 1
                                if working < 5:
                                    if str(day['opening_time'])+":00-"+str(day['closing_time'])+":00" not in roster[day['day']]:
                                        roster[day['day']][str(day['opening_time'])+":00-"+str(day['closing_time'])+":00" ] = [employee]
                                    elif roster[day['day']][str(day['opening_time'])+":00-"+str(day['closing_time'])+":00"]:
                                        roster[day['day']][str(day['opening_time'])+":00-"+str(day['closing_time'])+":00" ].append(employee)
            
            elif day['closing_time'] - day['opening_time'] <= 16:
                shift_length = day['closing_time'] - day['opening_time']
                if shift_length % 2 == 1:
                    shift_length += 1
                shift_length = int(round(shift_length)/2)
                for employee in employees:
                    if (
                        str(day['opening_time'])+":00-"+str(day['opening_time']+shift_length)+":00" not in roster[day['day']] or 
                        len(roster[day['day']][str(day['opening_time'])+":00-"+str(day['opening_time']+shift_length)+":00" ]) < day['min_workers']
                        ): 
                            if employee not in json.loads(day['unavailable']):
                                working = 0
                                for workday in roster:# check employee has less than 6 days 
                                    for value in roster[workday].values():
                                        if employee in value:
                                            working += 1
                                if working < 5:
                                    if str(day['opening_time'])+":00-"+str(day['opening_time']+shift_length)+":00" not in roster[day['day']]:
                                        roster[day['day']][str(day['opening_time'])+":00-"+str(day['opening_time']+shift_length)+":00" ] = [employee]
                                    elif roster[day['day']][str(day['opening_time'])+":00-"+str(day['opening_time']+shift_length)+":00"]:
                                        roster[day['day']][str(day['opening_time'])+":00-"+str(day['opening_time']+shift_length )+":00" ].append(employee)
                    elif (
                        str(day['closing_time']-shift_length)+":00-"+str(day['closing_time'])+":00" not in roster[day['day']] or 
                        len(roster[day['day']][str(day['closing_time']-shift_length)+":00-"+str(day['closing_time'])+":00" ]) < day['min_workers']
                        ): 
                            if employee not in json.loads(day['unavailable']):
                                working = 0
                                for workday in roster:
                                    for value in roster[workday].values():
                                        if employee in value:
                                            working += 1
                                if working < 5:
                                    if str(day['closing_time']-shift_length)+":00-"+str(day['closing_time'])+":00" not in roster[day['day']]:
                                        roster[day['day']][str(day['closing_time']-shift_length)+":00-"+str(day['closing_time'])+":00" ] = [employee]
                                    elif roster[day['day']][str(day['closing_time']-shift_length)+":00-"+str(day['closing_time'])+":00"]:
                                        roster[day['day']][str(day['closing_time']-shift_length)+":00-"+str(day['closing_time'])+":00" ].append(employee)
            
            elif day['closing_time'] - day['opening_time'] <= 24:
                shift_length = day['closing_time'] - day['opening_time']
                if shift_length % 3 != 0:
                    shift_length += 1
                shift_length = int(shift_length/3) + (shift_length % 3 > 0) # second parts evaluates to true and then +1 round up

                for employee in employees:
                    if (
                        str(day['opening_time'])+":00-"+str(day['opening_time']+shift_length)+":00" not in roster[day['day']] or 
                        len(roster[day['day']][str(day['opening_time'])+":00-"+str(day['opening_time']+shift_length)+":00" ]) < day['min_workers']
                        ): 
                            if employee not in json.loads(day['unavailable']):
                                working = 0
                                for workday in roster:# check employee has less than 6 days 
                                    
                                    for value in roster[workday].values():
                                        if employee in value:
                                            working += 1
                                if working < 5:
                                    if str(day['opening_time'])+":00-"+str(day['opening_time']+shift_length)+":00" not in roster[day['day']]:
                                        roster[day['day']][str(day['opening_time'])+":00-"+str(day['opening_time']+shift_length)+":00" ] = [employee]
                                    elif roster[day['day']][str(day['opening_time'])+":00-"+str(day['opening_time']+shift_length)+":00"]:
                                        roster[day['day']][str(day['opening_time'])+":00-"+str(day['opening_time']+shift_length )+":00" ].append(employee)
                    elif (
                        str(day['opening_time']+shift_length)+":00-"+str(day['closing_time']-shift_length)+":00" not in roster[day['day']] or 
                        len(roster[day['day']][str(day['opening_time']+shift_length)+":00-"+str(day['closing_time']-shift_length)+":00" ]) < day['min_workers']
                        ): 
                            if employee not in json.loads(day['unavailable']):
                                working = 0
                                for workday in roster:# check employee has less than 6 days 
                                    
                                    for value in roster[workday].values():
                                        if employee in value:
                                            working += 1
                                if working < 5:
                                    if str(day['opening_time']+shift_length)+":00-"+str(day['closing_time']-shift_length)+":00"  not in roster[day['day']]:
                                        roster[day['day']][str(day['opening_time']+shift_length)+":00-"+str(day['closing_time']-shift_length)+":00"  ] = [employee]
                                    elif roster[day['day']][str(day['opening_time']+shift_length)+":00-"+str(day['closing_time']-shift_length)+":00" ]:
                                        roster[day['day']][str(day['opening_time']+shift_length)+":00-"+str(day['closing_time']-shift_length)+":00" ].append(employee)
                    
                    elif (
                        str(day['closing_time']-shift_length)+":00-"+str(day['closing_time'])+":00" not in roster[day['day']] or 
                        len(roster[day['day']][str(day['closing_time']-shift_length)+":00-"+str(day['closing_time'])+":00" ]) < day['min_workers']
                        ): 
                            if employee not in json.loads(day['unavailable']):
                                working = 0
                                for workday in roster:# check employee has less than 6 days 
                                    
                                    for value in roster[workday].values():
                                        if employee in value:
                                            working += 1
                                if working < 5:
                                    if str(day['closing_time']-shift_length)+":00-"+str(day['closing_time'])+":00" not in roster[day['day']]:
                                        roster[day['day']][str(day['closing_time']-shift_length)+":00-"+str(day['closing_time'])+":00" ] = [employee]
                                    elif roster[day['day']][str(day['closing_time']-shift_length)+":00-"+str(day['closing_time'])+":00"]:
                                        roster[day['day']][str(day['closing_time']-shift_length)+":00-"+str(day['closing_time'])+":00" ].append(employee)    

        return roster