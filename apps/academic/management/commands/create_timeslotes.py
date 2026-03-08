# management/commands/create_timeslots.py
from django.core.management.base import BaseCommand
from datetime import time
from apps.attendance.models import TimeSlot

class Command(BaseCommand):
    help = 'Create time slots for school timetable (8:20 AM to 2:00 PM)'

    def handle(self, *args, **options):
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
        start_hour = 8
        start_minute = 20
        
        for day in days:
            current_hour = start_hour
            current_minute = start_minute
            period = 1
            
            while current_hour < 14 or (current_hour == 14 and current_minute == 0):
                # Class starts
                start_time = time(current_hour, current_minute)
                
                # Class ends (40 minutes later)
                end_minute = current_minute + 40
                end_hour = current_hour
                if end_minute >= 60:
                    end_minute -= 60
                    end_hour += 1
                end_time = time(end_hour, end_minute)
                
                # Create time slot
                TimeSlot.objects.get_or_create(
                    day=day,
                    period_number=period,
                    defaults={
                        'start_time': start_time,
                        'end_time': end_time
                    }
                )
                
                self.stdout.write(f"Created {day} Period {period}: {start_time} - {end_time}")
                
                # Next class starts after 5 minutes break
                current_minute = end_minute + 5
                current_hour = end_hour
                if current_minute >= 60:
                    current_minute -= 60
                    current_hour += 1
                
                period += 1
                
                # Stop if we reach or pass 2:00 PM
                if current_hour > 14 or (current_hour == 14 and current_minute > 0):
                    break
        
        self.stdout.write(self.style.SUCCESS('Successfully created time slots'))