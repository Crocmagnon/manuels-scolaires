from django.contrib import admin

from manuels.models import Teacher, Book, Level, Editor


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    pass


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    pass


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(Editor)
class EditorAdmin(admin.ModelAdmin):
    pass
