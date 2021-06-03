import csv

tf_times = {}
tf_out = {}

with open('TF Availability.csv', mode='r', encoding='utf-8-sig') as csv_file:
	csv_reader = csv.DictReader(csv_file)
	line_count = 0
	for row in csv_reader:
		time_available = []
		for i, column in enumerate(row):
			if i == 0:
				continue
			if row[column] != 'FALSE':
				time_available.append(row[column])
		tf_times[row['tf']] = time_available
		line_count += 1

for tf in tf_times:
	for i, timeslot in enumerate(tf_times[tf]):
		tf_times[tf][i] = {}
		tf_times[tf][i][timeslot.split(':')[0]] = timeslot.split(':')[1].strip().split(',')

for tf in tf_times:
	#print(tf)
	tf_out[tf] = {'timeslot':[],'already_bucketed':False,'students':[],'count':0,'cohort_number':999}
	for timeslot in tf_times[tf]:
		for inner_timeslot in timeslot:
			#print(inner_timeslot)
			for day_of_week in timeslot[inner_timeslot]:
				#print(day_of_week)
				tf_out[tf]['timeslot'].append(f'{day_of_week} {inner_timeslot}')

#print(tf_out)

time_total = {}

for tf in tf_out:
	#print(tf)
	for timeslot in tf_out[tf]:
		#print(timeslot)
		if timeslot in time_total:
			time_total[timeslot] += 1
		else:
			time_total[timeslot] = 0
	#print('\n')

#print('time,count')
#for time in time_total:
	#print(f'{time},{time_total[time]}')

#print(tf_out['Irma Gomez'])

# END TF AGGREGATION
# START TF BUCKETING
# Really depends on what student availability looks like...
# There are 34 TFs and 63 buckets
# The right TF buckets depend on student choices
# We need to see what student demand is for what timeslots in order to properly bucket in an optimized way

tf_buckets = {}
tf_times_smallest_to_largest = ["Thursdays 6 - 8 AM ET","Saturdays 10 PM - 12 AM ET","Mondays 6 - 8 AM ET","Tuesdays 6 - 8 AM ET","Sundays 6 - 8 AM ET","Sundays 10 PM - 12 AM ET","Thursdays 10 PM - 12 AM ET","Fridays 6 - 8 AM ET","Fridays 10 PM - 12 AM ET","Saturdays 2 - 4 PM ET","Saturdays 6 - 8 PM ET","Wednesdays 6 - 8 AM ET","Saturdays 6 - 8 AM ET","Saturdays 4 - 6 PM ET","Saturdays 8 - 10 PM ET","Sundays 8 - 10 AM ET","Sundays 6 - 8 PM ET","Mondays 10 PM - 12 AM ET","Tuesdays 10 PM - 12 AM ET","Wednesdays 10 PM - 12 AM ET","Sundays 2 - 4 PM ET","Sundays 4 - 6 PM ET","Sundays 8 - 10 PM ET","Tuesdays 8 - 10 AM ET","Thursdays 8 - 10 AM ET","Saturdays 8 - 10 AM ET","Saturdays 10 AM - 12 PM ET","Saturdays 12 - 2 PM ET","Sundays 10 AM - 12 PM ET","Sundays 12 - 2 PM ET","Fridays 8 - 10 PM ET","Mondays 8 - 10 AM ET","Wednesdays 8 - 10 AM ET","Fridays 8 - 10 AM ET","Thursdays 8 - 10 PM ET","Thursdays 10 AM - 12 PM ET","Fridays 6 - 8 PM ET","Mondays 8 - 10 PM ET","Wednesdays 10 AM - 12 PM ET","Fridays 10 AM - 12 PM ET","Tuesdays 8 - 10 PM ET","Wednesdays 8 - 10 PM ET","Fridays 12 - 2 PM ET","Mondays 10 AM - 12 PM ET","Tuesdays 10 AM - 12 PM ET","Thursdays 12 - 2 PM ET","Wednesdays 12 - 2 PM ET","Wednesdays 4 - 6 PM ET","Fridays 4 - 6 PM ET","Mondays 12 - 2 PM ET","Thursdays 6 - 8 PM ET","Fridays 2 - 4 PM ET","Mondays 6 - 8 PM ET","Tuesdays 12 - 2 PM ET","Wednesdays 2 - 4 PM ET","Mondays 2 - 4 PM ET","Wednesdays 6 - 8 PM ET","Tuesdays 6 - 8 PM ET","Thursdays 4 - 6 PM ET","Mondays 4 - 6 PM ET","Tuesdays 2 - 4 PM ET","Tuesdays 4 - 6 PM ET","Thursdays 2 - 4 PM ET"]

# Logic currently goes through buckets with fewest available TFs first, and assigns a TF to each bucket
# We have 34 TFs and 63 buckets, so will need to look at student data when it comes in to determine most TF buckets
cohort_counter = 0
for timebucket in reversed(tf_times_smallest_to_largest):
	for tf in tf_out:
		if timebucket in tf_out[tf]['timeslot'] and not tf_out[tf]['already_bucketed']:
			tf_buckets[tf] = timebucket
			tf_out[tf]['already_bucketed'] = True
			cohort_counter += 1
			tf_out[tf]['cohort_number'] = cohort_counter
			break

# print(f'TF Buckets: {tf_buckets}')

# END TF BUCKETING
# START STUDENT BUCKETING
students = {}
programs = {}
with open('student-sample-tf-distribution.csv', mode='r', encoding='utf-8-sig') as csv_file:
	csv_reader = csv.DictReader(csv_file)
	line_count = 0
	for row in csv_reader:
		students[row['email']] = {}
		students[row['email']]['time1'] = row['time1']
		students[row['email']]['time2'] = row['time2']
		students[row['email']]['time3'] = row['time3']
		students[row['email']]['program'] = row['program']
		if row['program'] in programs:
			programs[row['program']].append(row['email'])
		else:
			programs[row['program']] = [row['email']]
		students[row['email']]['concentration'] = row['concentration']
		students[row['email']]['student_bucketed'] = False
		students[row['email']]['cohort'] = False
		students[row['email']]['TF'] = ''
		students[row['email']]['third_choice_time_selected'] = False
		students[row['email']]['cohort_number'] = 999
		line_count += 1

#print(f'Programs: {programs}')

# Most important priority - timeslot
# Second most important - program
# Check timeslot and TF available
# Check program
# Check second choice and then program
# Check third choice and then program

# Loop through TF buckets
# Remember to remove "@ " when cleaning up student data
# Loop through each program to group students of programs together if possible
for tf in tf_buckets:
	for program in programs:
		for student in programs[program]:
			if students[student]['student_bucketed'] == False and tf_out[tf]['count'] <= 21 and students[student]['time1'] == tf_buckets[tf]:
				tf_out[tf]['students'].append(student)
				tf_out[tf]['count'] += 1
				students[student]['student_bucketed'] = True
				students[student]['cohort'] = tf_buckets[tf]
				students[student]['TF'] = tf
				students[student]['cohort_number'] = tf_out[tf]['cohort_number']

for tf in tf_buckets:
	for program in programs:
		for student in programs[program]:
			if students[student]['student_bucketed'] == False and tf_out[tf]['count'] <= 21 and students[student]['time2'] == tf_buckets[tf]:
				tf_out[tf]['students'].append(student)
				tf_out[tf]['count'] += 1
				students[student]['student_bucketed'] = True
				students[student]['cohort'] = tf_buckets[tf]
				students[student]['TF'] = tf
				students[student]['cohort_number'] = tf_out[tf]['cohort_number']

# Track if student was assigned based on their third choice
for tf in tf_buckets:
	for program in programs:
		for student in programs[program]:
			if students[student]['student_bucketed'] == False and tf_out[tf]['count'] <= 21 and students[student]['time3'] == tf_buckets[tf]:
				tf_out[tf]['students'].append(student)
				tf_out[tf]['count'] += 1
				students[student]['student_bucketed'] = True
				students[student]['cohort'] = tf_buckets[tf]
				students[student]['TF'] = tf
				students[student]['cohort_number'] = tf_out[tf]['cohort_number']
				students[row['email']]['third_choice_time_selected'] = True

# for tf in tf_out:
# 	print(f'{tf} ({tf_buckets[tf]}): {tf_out[tf]["students"]}')

unbucketed_count = 0
for student in students:
	if students[student]['student_bucketed'] == False:
		unbucketed_count += 1
		#print(f'Unbucketed: {student}, {students[student]["time1"]}')

# print(f'Unbucketed students: {unbucketed_count}')

# CSV output
print('student_email,student_cohort,cohort_tf,cohort_number,third_choice_time_selected,program')
for student in students:
	print(f'{student},{students[student]["cohort"]},{students[student]["TF"]},{students[student]["cohort_number"]},{students[student]["third_choice_time_selected"]},{students[student]["program"]}')

# Upload sample data

# Mock up a distribution that matches [TF availability?]
# Redistribute the sample data based on TF availability graph
# this is done

# List out programs, put the similar ones next to each other in the array?
# Add cohort number