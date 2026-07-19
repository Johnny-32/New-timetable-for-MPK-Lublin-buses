import timetable
from math import isnan


minute_list_container = []
difference_list_container = []
difference_list_container = []
group_list_for_a_timetable_period_container = []
not_matched_index_list_container = []
matched_frequency_list_container = []
breakpoint_list_container = []
tolerance = 2
predefined_frequency_list = [15, 20, 24, 30, 40, 45, 60]

for idx in range(len(timetable.df_list)):
    current_df = timetable.df_list[idx]

    # Filling a list with departure values in tuples: ('hour', 'minute')

    minute_list = []

    for key, value in current_df.items():
        for minute in value:
            if not (isnan(float(minute))):
                minute_list.append((key, minute))
    minute_list_container.append(minute_list)

    # Filling a list with differences between departures in tuples: ('hour:minute-hour:minute', 'difference')

    current_minute_list = minute_list_container[idx]
    difference_list = []
    for idx_m in range(len(current_minute_list) - 1):
        current_hour, current_minute = current_minute_list[idx_m]
        next_hour, next_minute = current_minute_list[idx_m + 1]
        difference_value = 60 * (int(next_hour) - int(current_hour)) + (int(next_minute) - int(current_minute))
        difference_key = f"{current_hour}:{current_minute}-{next_hour}:{next_minute}"
        difference_list.append((difference_key, difference_value))
    difference_list_container.append(difference_list)

    # Making groups based on frequency, not_matched differences are not put in a group, they're bare elements
    # ex. (diff. between dep. are skipped in this ex. for simplicity) 
    # [[32, 30], 27, [25, 24]]

    current_difference_list = difference_list_container[idx]
    group_list_for_a_timetable_period = []
    not_matched_index_list = []
    matched_frequency_list = []

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
                    matched_frequency_list.append(current_matched_freq)
                current_group = []
                
            current_group.append(current_item)
            current_matched_freq = matched_freq
        else:
            if current_group:
                group_list_for_a_timetable_period.append(current_group)
                matched_frequency_list.append(current_matched_freq)
                current_group = []
            
            group_list_for_a_timetable_period.append(current_item)

            idx_sublist = len(group_list_for_a_timetable_period) - 1
            not_matched_index_list.append(idx_sublist)

            current_matched_freq = None

    if current_group:
        group_list_for_a_timetable_period.append(current_group)
        matched_frequency_list.append(current_matched_freq)
        

    group_list_for_a_timetable_period_container.append(group_list_for_a_timetable_period)
    not_matched_index_list_container.append(not_matched_index_list)
    matched_frequency_list_container.append(matched_frequency_list)


    # Joining not matched elements into groups

    current_group_list = group_list_for_a_timetable_period_container[idx]

    idx_gr = 0
    while idx_gr < len(current_group_list):
        item = current_group_list[idx_gr]

        if not isinstance(item, list):
            left_is_group = (idx_gr > 0) and isinstance(current_group_list[idx_gr - 1], list)
            right_is_group = (idx_gr < len(current_group_list) - 1) and isinstance(current_group_list[idx_gr + 1], list)

            get_val = lambda x: x[1] if isinstance(x, tuple) else x

            current_val = get_val(item)

            # Finding a not matched element with exactly one neighbor that is a group
            # Then moving that not matched elemnent into a neighboring group
            if left_is_group ^ right_is_group:
                if left_is_group:
                    left_group = current_group_list[idx_gr - 1]
                    left_group.append(item)
                else:
                    right_group = current_group_list[idx_gr + 1]
                    right_group.insert(0, item)

                current_group_list.pop(idx_gr)
                continue 

            # Finding a not matched element, that has both neighbors, which are groups
            # Then moving that element to a group, which has a neighboring element, that is closer to a not matched element
            elif left_is_group and right_is_group:
                left_group = current_group_list[idx_gr - 1]
                right_group = current_group_list[idx_gr + 1]

                last_left_val = get_val(left_group[-1])
                first_right_val = get_val(right_group[0])

                diff_to_left = abs(current_val - last_left_val)
                diff_to_right = abs(current_val - first_right_val)

                if diff_to_left < diff_to_right:
                    left_group.append(item)
                    current_group_list.pop(idx_gr)
                elif diff_to_left > diff_to_right:
                    right_group.insert(0, item)
                    current_group_list.pop(idx_gr)
                # Joining two lists and an element, 
                # if the nearest elements from the neighboring groups have the same difference
                # ex. [..., group0, elem0, group1, ...] -> group0-elem0-group1
                else:
                    if last_left_val == first_right_val:
                        left_group.append(item)
                        left_group.extend(right_group)

                        current_group_list.pop(idx_gr)
                        current_group_list.pop(idx_gr)

                        matched_frequency_list.pop(idx_gr)
                    # In the future change this logic so it picks further from the unmatched element
                    # ex. [(32), 30], 27 ,[24, (23)], change this so it picks numbers in (), if they exist
                    else:
                        dist_to_left_elem = 1
                        dist_to_right_elem = 1
                        left_elem_value = get_val(left_group[-dist_to_left_elem])
                        right_elem_value = get_val(right_group[dist_to_left_elem - 1])
                        
                        while diff_to_left == diff_to_right:
                            dist_to_left_elem += 1
                            dist_to_right_elem += 1

                            left_elem_exists = True if len(left_group) >= dist_to_left_elem else False
                            right_elem_exists = True if len(right_group) > dist_to_right_elem else False
                            if left_elem_exists:
                                left_elem_value = get_val(current_group_list[-dist_to_left_elem])
                            else:
                                dist_to_left_elem -= 1
                            if right_elem_exists:
                                right_elem_value = get_val(current_group_list[dist_to_left_elem - 1])
                            else:
                                dist_to_right_elem -= 1

                            if dist_to_left_elem != 1 and dist_to_right_elem != 1:
                                diff_to_left = abs(current_val - left_elem_value)
                                diff_to_right = abs(current_val - right_elem_value)
                                if diff_to_left < diff_to_right:
                                    left_group.append(item)
                                    current_group_list.pop(idx_gr)
                                    break
                                elif diff_to_left > diff_to_right:
                                    right_group.insert(0, item)
                                    current_group_list.pop(idx_gr)
                                    break
                            # Very unlikely that this will ever execute
                            # If we reach the end elements and differences are still the same
                            # We move the non matched element to the group to the left
                            else:
                                left_group.append(item)
                                current_group_list.pop(idx_gr)
                                break

                continue

        idx_gr += 1

    matched_frequency_list_container.append(matched_frequency_list)

    # Making a list for breakpoints (timestamps when frequncies change)

    # print(current_group_list)
    # break

    breakpoint_list = []
    
    first_elem_in_first_group = current_group_list[0][0]
    first_elem_in_first_group_two_timestamps, first_elem_in_first_group_difference = first_elem_in_first_group
    first_elem_in_first_group_timestamp_list = first_elem_in_first_group_two_timestamps.split("-")
    first_elem_in_first_group_first_timestamp = first_elem_in_first_group_timestamp_list[0]
    breakpoint_list.append(first_elem_in_first_group_first_timestamp)
    

    for idx_gr in range(len(current_group_list)):
        last_elem_in_group = current_group_list[idx_gr][-1]
        last_elem_in_group_two_timestamps, last_elem_in_group_difference = last_elem_in_group
        last_elem_in_group_timestamp_list = last_elem_in_group_two_timestamps.split("-")
        last_elem_in_group_second_timestamp = last_elem_in_group_timestamp_list[1]
        breakpoint_list.append(last_elem_in_group_second_timestamp)

    breakpoint_list_container.append(breakpoint_list)

    print(f"Timetable nr {idx}")
    for idx_fr in range(len(breakpoint_list) + len(matched_frequency_list)):
        if idx_fr % 2 == 0:
            print(breakpoint_list[idx_fr // 2])
        else:
            print(matched_frequency_list[idx_fr // 2])
    print("\n")
            

    # print(breakpoint_list)
    # break
        
    # print("\n\n")

        
        # for current_item in current_group:
        #     current_two_timestamps, current_difference = current_item
            # print(current_two_timestamps)
            # print()


# for i in range(len(group_list_for_a_timetable_period_container[0])):
#     print(f"Group with frequency - {matched_frequency_list_container[0][i]}:\n{group_list_for_a_timetable_period_container[0][i]}\n")