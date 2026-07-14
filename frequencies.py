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


    current_difference_list = difference_list_container[idx]
    group_list = []
    group_list_for_a_timetable_period = []
    group_list_for_a_timetable_period_container = []
    not_matched_list = []
    group_frequency_list = []
    group_frequency_tuple = (0, 0)
    idx_of_a_group = 0

    for idx_d in range(len(current_difference_list)):
        current_two_timestamps, current_difference = current_difference_list[idx_d]
        two_timestamp_list = current_two_timestamps.split("-")
        first_timestamp = two_timestamp_list[0]
        next_timestamp = two_timestamp_list[1]

        

        # Problematyczny przypadek że grupy będą 15, 20, 15
        # Najlepiej bedzie to zrobic tak ze najpierw wszystkie roznice powrzucam do list z predefiniowanymi czestotliwosciami
        # Pozniej rozdzielę gdy next_timestamp w liscie bedzie sie rozil od first_timestamp w kolejnym elemencie listy
        # Wtedy w tym miejscu podzielę te listę na dwie listy
        # Ale jak będą bardziej skomplikowane przypadki to skad bedzie wiadomo na jakie miejsce dać nowo stworzoną listę
        # W takim razie należy poszukać innego sposobu
        # 
        # Trzeba użyć zmiennej next_group_switcher
        # Jakoś to trzeba zrobić że gdy zmienia się group_frequency to wtedy do kolejnej listy appendujemy
        # Może group frequency zrobić jako krotkę, która będzie trzymała poprzedni group_frequency i aktualny jakby
        # 
        # Struktury danych ktorych potrzebuję to
        # group_list -> jedna grupa różnic (np różnice z 24 czestotliwoscia) -> do group_list najlepiej przydałby się dostęp po indeksie
        # group_list_for_each_timetable_period -> będzie miała kilka elementów (np. 3) i elementy to będą group_list
        # group_list_for_each_timetable_container -> będzie miał tyle elementów ile jest timetable period (zazwyczaj 3)
        
        
        for predefined_frequency in predefined_frequency_list:
            if abs(current_difference - predefined_frequency) <= tolerance:
                first_elem_of_a_tuple, second_elem_of_a_tuple = group_frequency_tuple
                if group_frequency_tuple == (0, 0):
                    group_frequency_tuple = (predefined_frequency, predefined_frequency)
                else:
                    second_elem_of_a_tuple = predefined_frequency
                if first_elem_of_a_tuple != second_elem_of_a_tuple:
                    group_list_for_a_timetable_period.append(group_list)
                    group_list = []
                    first_elem_of_a_tuple = predefined_frequency
                group_frequency_list.append(predefined_frequency)
                group_list.append(current_difference_list[idx_d])
            else:
                not_matched_list.append(current_difference_list[idx_d])
        print(f"{group_list_for_a_timetable_period}\n")

    group_list_for_a_timetable_period_container.append(group_list_for_a_timetable_period)
