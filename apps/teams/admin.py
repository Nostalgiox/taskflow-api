from django.contrib import admin

from .models import Membership, Team


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [MembershipInline]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("team", "user", "role", "joined_at")
    list_filter = ("role",)
