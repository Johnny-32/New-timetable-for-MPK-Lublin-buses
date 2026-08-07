## How are frequencies calculated

1. The difference is calculated between one departure time and the next.
   For example:

   | 5  |
   |----|
   | 05 |
   | 37 |
    
   37 - 05 = 32
   So the result is -> 5:05-5:37 - 32  
   And the difference is 32 minutes.

2. Now we can put these differences into groups based on their predefined frequencies and tolerance value.  
   Predefined frequencies are frequencies, that are commonly used by MPK Lublin lines and these are (15, 20, 24, 30, 40, 60 minutes).  
   Tolerance is a value that represents maximum difference between calculated difference in point 1. and a predefined frequency.  
   If a difference between a calculated difference in point 1. and a predefined frequency is bigger than the tolerance, it will be marked as a not matched element.

3. Now that we have groups and not matched elements, we can add not matched elements to groups, but before that let's put them into following categories: 
   Cat 1. Not matched elements that are surrounded by groups (ex. [..., group0, notmatched0, group1, ...])  
   Cat 2. Not matched elements that have a neighboring element which is a group (either to the left or to the right) (ex. [..., group0, notmatched0, notmatched1, ...])  
   Cat 3. Elements that are surrounded by not matched list elements (ex. [..., notmatched0, notmatched1, notmatched2, ...])  
   So my soultion is to append every element to a group in following steps:  
   If we find an element in Cat 1. we append it to the group that has the element that is the closest to an unmatched element  
   ex. [[..., 30], 27, [25, ...]] we append that element to the group to the right, beacuse |27 - 30| > |27 - 25|  
   If we find an element in Cat 2. we append that element to the group that neighbors this element  
   By doing this two steps we should transform elements in Cat 3. to an element in either Cat 1. or Cat 2.

4. Now we have a list of groups with corresponding frequencies

## Pros of this algorithm
- It's pretty efficient and simple
- Every departure has a assigned frequency, which makes it easy to plot into for example a graph

## Flaws
- It doesn't work with frequencies that are not clock-face based like 42 minutes
- It doesn't work with irregular departure times
- Every departure has a assigned frequency, which isn't always a reality, when it comes to irregular departures
- Doesn't work with very high frequencies like 5 minutes, beacuse tolerance would need to be dynamic (though I'm not sure it would work)

## Example of the algorithm
Example 1. (Made in July 2026 - Holiday timetable)  
Line: 32  
Direction: Daszyńskiego  
Bus stop: Plac Litewskiego 02 (Index - 1022)  
Timetable:  

     5   6    7    8   9   10  11   12  13   14  15   16   17   18   19   20   21   22   23 
    05  07   26   15  02   14  02   14  02   14  02   17   04   05   03   03   06   06   05
    37  34   51   38  26   38  26   38  26   38  29   41   35   33   33   36   36   36  NaN
   NaN  59  NaN  NaN  50  NaN  50  NaN  50  NaN  53  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN
