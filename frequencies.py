# Calculating approximate frequencies
# The algorithm will work by:
# 1. Reading values of two minute values at a time and then calculating the frequency by subtracting each minute with the next 
#    and adding 60 to the result if it's a non-positive number, so that the algorithm works with subtracting minutes that are associated with different hours,
#    results will be stored in a dictionary with key that indicates hours and minutes that the minutes were subtracted (ex. 5:09 and 5:39 -> '5:09 - 5:39': '30') (ex. 5:39 and 6:09 -> '5:39 - 6:09': '30')
# ex. 1.1  6   mod 60 (59 - 29) = 30
#         29
#         59
# 
# ex. 1.2  5   6   27 - 29 = -2 (beacuse it's a non-positive number we add 60 the the result) -2 + 60 = 58
#         29  27
# 
# 2. To have a x minute frequency label the line needs to have departures every x +- y minutes,
#    where x is the frequency and y is the tolerance for said frequency
#    for ex. if a line has a 24 minute fruquency label it needs to have departures every 22-26 minutes, if tolerance is 2 minutes,
#    as a base a tolerance of 2 minutes will be used,
#    frequency for a period of time must be one of the predefined frequencies:
#    (15, 20, 24, 30, 40, 45, 60, >60)
#    ??? Maybe if a frequency for a period of time sways to far from a predefined frequency it will be put into something like this:
#    if a calculated frequency is 35 minutes with big fluctuations, maybe it can be put into 30-40 frequency
#    
# 3. The differences will be put into groups based on their differences, if the difference between two diiferences is <= tolerance 
#    and it the diff of diffs. is within tolerance of a predefined frequency these differences will be put in a group
# 
# 4. To end a group, a difference between differences needs to be larger than the tolerance
#    To start another group the diff between diffs. needs to fall be <= tolerance
#    ??? If it isn't then probably we'll need to up the tolernace temporarily
# 
# 5. From these groups we can skip "End of group 1." relation and pick the last from difference from group x and the first from group x+1, we'll refer to them as key differences
# 
# 6. Using these two differences we can make out a breakpoint between two frequency groups by checking the keys from key differences 
#    and extracting the first timestamp from the first key difference and the second timestamp from the second one, in result we we'll have a breakpoint
# 
# 7. At the end we can plot the data into something like this: first departure - frequency - breakpoint - frequency - breakpoint - ... - frequency - last departure
# 
# 
# Data structures used for storing this data:
# diffs -> dictionary that will store differences time between departures (ex. one elem -> '5:37-5:05': 32)
# group_container -> list that will contain groups
# group_container[i] -> list that will contained diffs that are grouped (so like in example it will be group 1. ...)
# breakpoint_list -> list that will contain breakpoints
# 
# 
# 
# 
# Example 1. (Made in July 2026 - Holiday timetable) ------------------------------------------------------------------------------------------------
# Line: 32
# Direction: Daszyńskiego
# Bus stop: Plac Litewskiego 02 (Index - 1022)
# Timetable:
# 
#     5   6    7    8   9   10  11   12  13   14  15   16   17   18   19   20   21   22   23 
#    05  07   26   15  02   14  02   14  02   14  02   17   04   05   03   03   06   06   05
#    37  34   51   38  26   38  26   38  26   38  29   41   35   33   33   36   36   36  NaN
#   NaN  59  NaN  NaN  50  NaN  50  NaN  50  NaN  53  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN
# 
# In this example we will be sticking to hours 5-9
# 1. Calculating differences
# 5:37 - 5:05 = 32
# 6:07 - 5:37 = -30 + 60 = 30
# 6:34 - 6:07 = 27
# 6:59 - 6:34 = 25
# 7:26 - 6:59 = -33 + 60 = 27
# 7:51 - 7:26 = 25
# 8:15 - 7:51 = -36 + 60 = 24
# 8:38 - 8:15 = 23
# 9:02 - 8:38 = 24
# 9:26 - 9:02 = 24
# 9:50 - 9:26 = 24
# 
# So using our common sense we can see that frequencies are:
# 5:05 - 6:07 --- 30 minutes
# 6:07 - 7:51 --- it makes to make it 24 minutes, but in reality it's 26 minutes
# 7:51 - 9:50 --- 24 minutes
# 
# Now we can group the differences, let's say that the tolerance between differences is 2 minutes
# 32 - 30 = 2 -> Start of group 1.
# 30 - 27 = 3 -> End of group 1.
# 27 - 25 = 2 -> Start of group 2.
# 25 - 27 = 2 -> Both in group 2.
# 27 - 25 = 2 -> Both in group 2
# 25 - 24 = 1 -> Both in group 2
# 24 - 23 = 1 -> Both in group 2
# 23 - 24 = 1 -> Both in group 2
# 24 - 24 = 0 -> Both in group 2
# 24 - 24 = 0 -> Both in group 2
# 
# So now we have 2 groups and now we can calculate the mean from all values in each group and see which predefined frequency (for ex. 20, 24, 30, ...) will be the closest to the mean and assign that label
# for ex. group 1. (32 + 30) / 2 = 31 -> which is close to 30, so we will asign a 30 minute frequency label to that group
# group 2. after calculations will have 24 minute frequency label
# 
# We can see that the last difference for the group 1 is 30, and the first for the group 2. is 27,
# so that means if we skip "End of group 1." we have all the differences in correct groups (obviously we need to delete duplicates)
# 
# Now we need to extract timestamps from key differences (30 and 27)
# We can do this by - extracting the key from dictionary:
# in group 1. we have a key difference of 30, which translates to 6:07 - 5:37
# in group 2. we have a key difference of 27, which translates to 6:34 - 6:07
# 
# Beacuse the first number of the 1. group and the second number of the 2. group matches, that means that 6:07 will be a breakpoint for frequency labels
# 
# As a result we got frequencies which are the same as we got above using common sense
# 
# ??? Maybe add calculating frequencies by getting the timetable from the first stop of a route, beacuse the departures there are more consistent

import timetable
from math import isnan

# for i in range(len(timetable.table_hour_list_container)):
#     print(timetable.df_list[i])
#     print("\n")

minute_list_container = []
difference_list_container = []
difference_list_container = []
group_list_for_a_timetable_period_container = []
not_matched_index_list_container = []
tolerance = 2
predefined_frequency_list = [15, 20, 24, 30, 40, 45, 60]

for idx in range(len(timetable.df_list)):
    current_df = timetable.df_list[idx]
    # print(current_df)

    # Filling a list with minute values

    minute_list = []

    for key, value in current_df.items():
        for minute in value:
            if not (isnan(float(minute))):
                minute_list.append((key, minute))
    minute_list_container.append(minute_list)

    # Filling a list with differences in tuples (hour:minute-hour:minute) in minutes between departures

    current_minute_list = minute_list_container[idx]
    difference_list = []
    for idx_m in range(len(current_minute_list) - 1):
        current_hour, current_minute = current_minute_list[idx_m]
        next_hour, next_minute = current_minute_list[idx_m + 1]
        difference_value = 60 * (int(next_hour) - int(current_hour)) + (int(next_minute) - int(current_minute))
        difference_key = f"{current_hour}:{current_minute}-{next_hour}:{next_minute}"
        difference_list.append((difference_key, difference_value))
    difference_list_container.append(difference_list)


    # Making groups based on frequency, for now adding not matched frequencies to a separate list,
    # but in the future planning to add these items as one elem. lists (or longer),
    # I would have to add a flag to each of these not matched lists

    current_difference_list = difference_list_container[idx]
    group_list_for_a_timetable_period = []
    not_matched_index_list = []

    current_group = []
    current_matched_freq = None

    for current_item in current_difference_list:
        current_two_timestamps, current_difference = current_item
        
        matched_freq = None
        for predefined_freq in predefined_frequency_list:
            if abs(current_difference - predefined_freq) <= tolerance:
                matched_freq = predefined_freq
                break
                
        if matched_freq is not None:
            if current_matched_freq is not None and matched_freq != current_matched_freq:
                if current_group:
                    group_list_for_a_timetable_period.append(current_group)
                current_group = []
                
            current_group.append(current_item)
            current_matched_freq = matched_freq
        else:
            if current_group:
                group_list_for_a_timetable_period.append(current_group)
                current_group = []
            
            group_list_for_a_timetable_period.append(current_item)

            idx_sublist = len(group_list_for_a_timetable_period) - 1
            not_matched_index_list.append(idx_sublist)

            current_matched_freq = None

    if current_group:
        group_list_for_a_timetable_period.append(current_group)

    group_list_for_a_timetable_period_container.append(group_list_for_a_timetable_period)
    not_matched_index_list_container.append(not_matched_index_list)


print(f"Groups:\n{group_list_for_a_timetable_period_container[0]}\n")
print(f"Indexes of not matched elements:\n{not_matched_index_list_container[0]}")
