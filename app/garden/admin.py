from django.contrib import admin
from .models import (
    Garden, GardenAccess, Valve, Power, Pump, Schedule, SystemLog,
    WaterUsage, PowerConsumption
)


@admin.register(Garden)
class GardenAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'created_at')
    search_fields = ('name', 'location')
    list_filter = ('created_at',)


class GardenAccessInline(admin.TabularInline):
    model = GardenAccess
    extra = 1


@admin.register(GardenAccess)
class GardenAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'garden', 'role')
    list_filter = ('role', 'garden')
    search_fields = ('user__email', 'garden__name')


@admin.register(Valve)
class ValveAdmin(admin.ModelAdmin):
    list_display = ('garden', 'number', 'status', 'duration', 'last_active')
    list_filter = ('status', 'garden')
    list_editable = ('status', 'duration')


@admin.register(Power)
class PowerAdmin(admin.ModelAdmin):
    list_display = ('id', 'garden', 'status', 'last_status_change')
    list_display_links = ('id',)
    list_editable = ('status',)
    list_filter = ('garden', 'status')


@admin.register(Pump)
class PumpAdmin(admin.ModelAdmin):
    list_display = ('id', 'garden', 'status', 'last_status_change')
    list_display_links = ('id',)
    list_editable = ('status',)
    list_filter = ('garden', 'status')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('garden', 'target', 'startTime', 'duration', 'repeat', 'isActive')
    list_filter = ('garden', 'repeat', 'isActive')
    list_editable = ('isActive',)
    search_fields = ('target',)


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('garden', 'event', 'timestamp', 'source')
    list_filter = ('garden', 'source', 'timestamp')
    search_fields = ('event',)
    date_hierarchy = 'timestamp'


@admin.register(WaterUsage)
class WaterUsageAdmin(admin.ModelAdmin):
    list_display = ('garden', 'period', 'valve1', 'valve2', 'valve3', 'timestamp')
    list_filter = ('garden', 'timestamp')
    search_fields = ('period',)


@admin.register(PowerConsumption)
class PowerConsumptionAdmin(admin.ModelAdmin):
    list_display = ('garden', 'time', 'consumption', 'date')
    list_filter = ('garden', 'date')
    date_hierarchy = 'date' 