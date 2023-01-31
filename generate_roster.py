import random

roster = {
    'mon': [
        [6,22], # opening hours
        2, # min workers
        [], # cant work
        {}# {'6:00-(6+()):00': []}
    ],
    'tue': [
        [6,14], # opening hours
        7, # min workers
        ["klaas"], # cant work
        {}# {'6:00-(6+()):00': []}
    ],
    'wed': [
        [0,22], # opening hours
        2, # min workers
        [], # cant work
        {}# {'6:00-(6+()):00': []}
    ],
    'thu': [
        [0,22], # opening hours
        2, # min workers
        [], # cant work
        {}# {'6:00-14:00': ['kevin', 'tommy'], '14:00-22:00': ['klaas', 'cherry']}
    ],
    'fri': [
        [0,8], # opening hours
        7, # min workers
        [], # cant work
        {}# {'6:00-(6+()):00': []}
    ],
    'sat': [
        [0,8], # opening hours
        7, # min workers
        [], # cant work
        {}# {'6:00-(6+()):00': []}
    ],
    'sun': [
        [0,8], # opening hours
        7, # min workers
        [], # cant work
        {}# {'6:00-(6+()):00': []}
    ],
}


roster1 = {
    'mon': [
        [6,14], # opening hours
        7, # min workers
        [], # cant work
        {}# {'6:00-(6+()):00': []}
    ],
    'tue': [
        [6,14], # opening hours
        7, # min workers
        [], # cant work
        {}# {'6:00-(6+()):00': []}
    ],
    'wed': [
        [0,7], # opening hours
        7, # min workers
        [], # cant work
        {}# {'6:00-(6+()):00': []}
    ],
    'thu': [
        [0,7], # opening hours
        7, # min workers
        [], # cant work
        {}# {'6:00-14:00': ['kevin', 'tommy'], '14:00-22:00': ['klaas', 'cherry']}
    ],
    'fri': [
        [0,8], # opening hours
        7, # min workers
        [], # cant work
        {}# {'6:00-(6+()):00': []}
    ],
    'sat': [
        [0,8], # opening hours
        7, # min workers
        [], # cant work
        {}# {'6:00-(6+()):00': []}
    ],
    'sun': [
        [0,8], # opening hours
        7, # min workers
        [], # cant work
        {}# {'6:00-(6+()):00': []}
    ]
}

employees = ["ben", "aodh", "emma", "tommy", "cherry", "klaas", "patrick"]

for day in roster:
    random.shuffle(employees)
    if roster[day][0][1] - roster[day][0][0] <= 8:
        for employee in employees:
            if (
                str(roster[day][0][0])+":00-"+str(roster[day][0][1])+":00" not in roster[day][3] or 
                len(roster[day][3][str(roster[day][0][0])+":00-"+str(roster[day][0][1])+":00" ]) < roster[day][1]
                ): 
                    if employee not in roster[day][2]:
                        working = 0
                        for workday in roster:# check employee has less than 6 days 
                            
                            #print( roster[workday][3].values())
                            for value in roster[workday][3].values():
                                if employee in value:
                                    working += 1
                        if working < 5:
                            if str(roster[day][0][0])+":00-"+str(roster[day][0][1])+":00" not in roster[day][3]:
                                roster[day][3][str(roster[day][0][0])+":00-"+str(roster[day][0][1])+":00" ] = [employee]
                            elif roster[day][3][str(roster[day][0][0])+":00-"+str(roster[day][0][1])+":00"]:
                                roster[day][3][str(roster[day][0][0])+":00-"+str(roster[day][0][1])+":00" ].append(employee)
    
    elif roster[day][0][1] - roster[day][0][0] <= 16:
        shift_length = roster[day][0][1] - roster[day][0][0]
        if shift_length % 2 == 1:
            shift_length += 1
        shift_length = int(round(shift_length)/2)
        for employee in employees:
            if (
                str(roster[day][0][0])+":00-"+str(roster[day][0][0]+shift_length)+":00" not in roster[day][3] or 
                len(roster[day][3][str(roster[day][0][0])+":00-"+str(roster[day][0][0]+shift_length)+":00" ]) < roster[day][1]
                ): 
                    if employee not in roster[day][2]:
                        working = 0
                        for workday in roster:# check employee has less than 6 days 
                            
                            #print( roster[workday][3].values())
                            for value in roster[workday][3].values():
                                if employee in value:
                                    working += 1
                        if working < 5:
                            if str(roster[day][0][0])+":00-"+str(roster[day][0][0]+shift_length)+":00" not in roster[day][3]:
                                roster[day][3][str(roster[day][0][0])+":00-"+str(roster[day][0][0]+shift_length)+":00" ] = [employee]
                            elif roster[day][3][str(roster[day][0][0])+":00-"+str(roster[day][0][0]+shift_length)+":00"]:
                                roster[day][3][str(roster[day][0][0])+":00-"+str(roster[day][0][0]+shift_length )+":00" ].append(employee)
            elif (
                str(roster[day][0][1]-shift_length)+":00-"+str(roster[day][0][1])+":00" not in roster[day][3] or 
                len(roster[day][3][str(roster[day][0][1]-shift_length)+":00-"+str(roster[day][0][1])+":00" ]) < roster[day][1]
                ): 
                    if employee not in roster[day][2]:
                        working = 0
                        for workday in roster:# check employee has less than 6 days 
                            
                            #print( roster[workday][3].values())
                            for value in roster[workday][3].values():
                                if employee in value:
                                    working += 1
                        if working < 5:
                            if str(roster[day][0][1]-shift_length)+":00-"+str(roster[day][0][1])+":00" not in roster[day][3]:
                                roster[day][3][str(roster[day][0][1]-shift_length)+":00-"+str(roster[day][0][1])+":00" ] = [employee]
                            elif roster[day][3][str(roster[day][0][1]-shift_length)+":00-"+str(roster[day][0][1])+":00"]:
                                roster[day][3][str(roster[day][0][1]-shift_length)+":00-"+str(roster[day][0][1])+":00" ].append(employee)
    
    elif roster[day][0][1] - roster[day][0][0] <= 24:
        shift_length = roster[day][0][1] - roster[day][0][0]
        if shift_length % 3 != 0:
            shift_length += 1
        shift_length = int(shift_length/3) + (shift_length % 3 > 0) # second parts evaluates to true and then +1 round up

        for employee in employees:
            if (
                str(roster[day][0][0])+":00-"+str(roster[day][0][0]+shift_length)+":00" not in roster[day][3] or 
                len(roster[day][3][str(roster[day][0][0])+":00-"+str(roster[day][0][0]+shift_length)+":00" ]) < roster[day][1]
                ): 
                    if employee not in roster[day][2]:
                        working = 0
                        for workday in roster:# check employee has less than 6 days 
                            
                            #print( roster[workday][3].values())
                            for value in roster[workday][3].values():
                                if employee in value:
                                    working += 1
                        if working < 5:
                            if str(roster[day][0][0])+":00-"+str(roster[day][0][0]+shift_length)+":00" not in roster[day][3]:
                                roster[day][3][str(roster[day][0][0])+":00-"+str(roster[day][0][0]+shift_length)+":00" ] = [employee]
                            elif roster[day][3][str(roster[day][0][0])+":00-"+str(roster[day][0][0]+shift_length)+":00"]:
                                roster[day][3][str(roster[day][0][0])+":00-"+str(roster[day][0][0]+shift_length )+":00" ].append(employee)
            elif (
                str(roster[day][0][0]+shift_length)+":00-"+str(roster[day][0][1]-shift_length)+":00" not in roster[day][3] or 
                len(roster[day][3][str(roster[day][0][0]+shift_length)+":00-"+str(roster[day][0][1]-shift_length)+":00" ]) < roster[day][1]
                ): 
                    if employee not in roster[day][2]:
                        working = 0
                        for workday in roster:# check employee has less than 6 days 
                            
                            #print( roster[workday][3].values())
                            for value in roster[workday][3].values():
                                if employee in value:
                                    working += 1
                        if working < 5:
                            if str(roster[day][0][0]+shift_length)+":00-"+str(roster[day][0][1]-shift_length)+":00"  not in roster[day][3]:
                                roster[day][3][str(roster[day][0][0]+shift_length)+":00-"+str(roster[day][0][1]-shift_length)+":00"  ] = [employee]
                            elif roster[day][3][str(roster[day][0][0]+shift_length)+":00-"+str(roster[day][0][1]-shift_length)+":00" ]:
                                roster[day][3][str(roster[day][0][0]+shift_length)+":00-"+str(roster[day][0][1]-shift_length)+":00" ].append(employee)
            
            elif (
                str(roster[day][0][1]-shift_length)+":00-"+str(roster[day][0][1])+":00" not in roster[day][3] or 
                len(roster[day][3][str(roster[day][0][1]-shift_length)+":00-"+str(roster[day][0][1])+":00" ]) < roster[day][1]
                ): 
                    if employee not in roster[day][2]:
                        working = 0
                        for workday in roster:# check employee has less than 6 days 
                            
                            #print( roster[workday][3].values())
                            for value in roster[workday][3].values():
                                if employee in value:
                                    working += 1
                        if working < 5:
                            if str(roster[day][0][1]-shift_length)+":00-"+str(roster[day][0][1])+":00" not in roster[day][3]:
                                roster[day][3][str(roster[day][0][1]-shift_length)+":00-"+str(roster[day][0][1])+":00" ] = [employee]
                            elif roster[day][3][str(roster[day][0][1]-shift_length)+":00-"+str(roster[day][0][1])+":00"]:
                                roster[day][3][str(roster[day][0][1]-shift_length)+":00-"+str(roster[day][0][1])+":00" ].append(employee)    

print(roster)